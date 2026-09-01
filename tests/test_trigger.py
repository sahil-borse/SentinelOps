"""S1 — generation, the state machine, escalation, routing and exceptions."""

from datetime import date, datetime, timedelta

import pytest

from sentinelops.entities import ComplianceException, EvidenceSubmission
from sentinelops.repositories import repositories
from sentinelops.stages.trigger import (
    DEFAULT_POLICY,
    SETTLED,
    SchedulePolicy,
    advance_calendar,
    covers,
    instance_id,
    last_cycle_date,
    owner_chain,
    run_cycle,
)
from sentinelops.synth import generate_corpus, seed_database

END_OF_STORY = date(2027, 3, 31)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture()
def seeded(conn, corpus):
    seed_database(conn, corpus)
    return conn


# --- generation ------------------------------------------------------------

def test_a_full_year_generates_an_instance_per_open_period(seeded, corpus):
    result = run_cycle(seeded, END_OF_STORY)
    instances = repositories(seeded)["instances"].list()

    # 64 applicable pairs across their frequencies, less the 3 periods that
    # approved exceptions excuse.
    assert len(instances) == 343
    assert len(result.created) == 343
    assert len(result.suppressed) == 3


def test_nothing_generates_before_its_period_opens(seeded):
    run_cycle(seeded, date(2026, 1, 20))
    instances = repositories(seeded)["instances"].list()
    periods = {i.period for i in instances}

    assert periods == {"2026-01", "2026-Q1", "2026"}
    assert not any(i.period == "2026-02" for i in instances)


def test_advancing_the_calendar_reveals_more_checks(seeded):
    run_cycle(seeded, date(2026, 1, 20))
    after_january = len(repositories(seeded)["instances"].list())

    advance_calendar(seeded, 60)
    after_march = len(repositories(seeded)["instances"].list())

    assert after_march > after_january


def test_instance_ids_are_derived_and_readable(seeded):
    run_cycle(seeded, date(2026, 4, 30))
    assert instance_id("CTRL-ACCESS-REVIEW", "AREA-CUSTOPS", "2026-Q1") == (
        "CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1"
    )
    assert repositories(seeded)["instances"].get("CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1")


def test_due_dates_come_from_period_close_plus_grace(seeded, corpus):
    run_cycle(seeded, END_OF_STORY)
    instance = repositories(seeded)["instances"].get("CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1")
    control = next(c for c in corpus.controls if c.id == "CTRL-ACCESS-REVIEW")
    assert instance.due_date == date(2026, 3, 31) + timedelta(days=control.grace_days)


def test_every_instance_lands_on_an_applicable_pair(seeded, corpus):
    run_cycle(seeded, END_OF_STORY)
    pairs = set(corpus.applicable_pairs)
    for instance in repositories(seeded)["instances"].list():
        assert (instance.control_id, instance.process_area_id) in pairs


# --- idempotency -----------------------------------------------------------

def test_running_the_same_cycle_twice_creates_nothing_new(seeded):
    first = run_cycle(seeded, END_OF_STORY)
    count = len(repositories(seeded)["instances"].list())

    second = run_cycle(seeded, END_OF_STORY)
    assert second.created == []
    assert len(repositories(seeded)["instances"].list()) == count
    assert len(first.created) == 343


def test_five_cycles_over_the_year_produce_the_same_instances_as_one(conn, corpus):
    seed_database(conn, corpus)
    for as_of in (date(2026, 3, 1), date(2026, 6, 1), date(2026, 9, 1),
                  date(2026, 12, 1), END_OF_STORY):
        run_cycle(conn, as_of)
    incremental = {i.id for i in repositories(conn)["instances"].list()}

    other = conn  # a second database, seeded identically
    import sentinelops.db as db_module

    fresh = db_module.connect(":memory:")
    seed_database(fresh, corpus)
    run_cycle(fresh, END_OF_STORY)
    one_shot = {i.id for i in repositories(fresh)["instances"].list()}
    fresh.close()

    assert incremental == one_shot
    assert other is conn


def test_no_duplicate_control_area_period_survives(seeded):
    run_cycle(seeded, END_OF_STORY)
    run_cycle(seeded, END_OF_STORY)
    keys = [
        (i.control_id, i.process_area_id, i.period)
        for i in repositories(seeded)["instances"].list()
    ]
    assert len(keys) == len(set(keys))


# --- the state machine -----------------------------------------------------

def test_a_new_instance_starts_pending(seeded):
    run_cycle(seeded, date(2026, 2, 10))
    instance = repositories(seeded)["instances"].get("CHK-CHANGE-MGMT-FINREP-2026-02")
    assert instance.status == "pending"


def test_evidence_moves_an_instance_to_submitted(seeded):
    run_cycle(seeded, END_OF_STORY)
    submitted = [
        i for i in repositories(seeded)["instances"].list() if i.status == "submitted"
    ]
    assert submitted
    submissions = {
        (s.control_id, s.process_area_id, s.period)
        for s in repositories(seeded)["submissions"].list()
    }
    for instance in submitted:
        assert (instance.control_id, instance.process_area_id, instance.period) in submissions


def test_a_missing_submission_goes_overdue(seeded):
    """CTRL-CUST-COMPLAINTS / AREA-CUSTOPS / 2026-07 is a corpus 'missing'."""
    run_cycle(seeded, END_OF_STORY)
    instance = repositories(seeded)["instances"].get(
        "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    )
    assert instance.status == "overdue"
    assert instance.due_date == date(2026, 8, 15)


def test_nothing_goes_overdue_before_its_due_date(seeded):
    run_cycle(seeded, date(2026, 8, 1))
    instance = repositories(seeded)["instances"].get(
        "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    )
    assert instance.status == "pending"


def test_every_status_is_one_the_state_machine_declares(seeded):
    run_cycle(seeded, END_OF_STORY)
    statuses = {i.status for i in repositories(seeded)["instances"].list()}
    assert statuses <= {"pending", "submitted", "assessed", "overdue", "waived"}


def test_an_exception_granted_later_waives_an_open_instance(conn, corpus):
    """`waived` is reachable: the corpus never needs it, so build the case."""
    seed_database(conn, corpus)
    run_cycle(conn, date(2026, 2, 10))
    repo = repositories(conn)
    instance = repo["instances"].get("CHK-CHANGE-MGMT-FINREP-2026-02")
    assert instance.status == "pending"

    repo["exceptions"].add(
        ComplianceException(
            id="EXC-LATE",
            control_id="CTRL-CHANGE-MGMT",
            process_area_id="AREA-FINREP",
            rationale="Change freeze agreed after the period opened.",
            approved_by="Finance Control Board",
            granted_at=date(2026, 2, 1),
            expires_at=date(2026, 12, 31),
            status="active",
        )
    )
    run_cycle(conn, date(2026, 3, 10))
    assert repo["instances"].get("CHK-CHANGE-MGMT-FINREP-2026-02").status == "waived"
    assert "waived" in SETTLED


def test_a_settled_instance_is_left_alone(conn, corpus):
    seed_database(conn, corpus)
    run_cycle(conn, date(2026, 2, 10))
    repo = repositories(conn)
    instance = repo["instances"].get("CHK-CHANGE-MGMT-FINREP-2026-02")
    instance.status = "assessed"
    repo["instances"].update(instance)

    run_cycle(conn, END_OF_STORY)
    assert repo["instances"].get("CHK-CHANGE-MGMT-FINREP-2026-02").status == "assessed"


# --- escalation ------------------------------------------------------------

def test_overdue_escalates_one_level_per_interval(seeded):
    target = "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"  # due 2026-08-15, never filed
    run_cycle(seeded, date(2026, 8, 20))            # 5 days over: no escalation
    assert _levels(seeded, target) == []

    run_cycle(seeded, date(2026, 8, 30))            # 15 days over: level 1
    assert _levels(seeded, target) == [1]

    run_cycle(seeded, date(2026, 9, 14))            # 30 days over: level 2
    assert _levels(seeded, target) == [1, 2]


def test_escalation_does_not_repeat_on_later_cycles(seeded):
    target = "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    for as_of in (date(2026, 9, 14), date(2026, 10, 14), date(2026, 11, 14)):
        run_cycle(seeded, as_of)
    assert _levels(seeded, target) == [1, 2]


def test_escalation_stops_at_the_top_of_the_chain(seeded):
    run_cycle(seeded, END_OF_STORY)
    target = "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    assert _levels(seeded, target) == [1, 2]
    assert max(_levels(seeded, target)) == DEFAULT_POLICY.max_escalation_level


def test_escalation_walks_up_the_owner_chain(seeded, corpus):
    run_cycle(seeded, END_OF_STORY)
    area = next(a for a in corpus.areas if a.id == "AREA-CUSTOPS")
    chain = owner_chain(area)
    events = [
        e
        for e in repositories(seeded)["audit"].read_for(
            "CheckInstance", "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
        )
        if e.action == "check_instance_escalated"
    ]
    assert [e.detail["escalated_to"] for e in events] == [chain[1][0], chain[2][0]]
    assert events[-1].detail["team"] == "Group Compliance"


def test_the_escalation_interval_is_configurable(seeded):
    policy = SchedulePolicy(escalate_after_days=3)
    run_cycle(seeded, date(2026, 8, 22), policy=policy)  # 7 days over -> level 2
    assert _levels(seeded, "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07") == [1, 2]


def _levels(conn, instance_key):
    return [
        e.detail["level"]
        for e in repositories(conn)["audit"].read_for("CheckInstance", instance_key)
        if e.action == "check_instance_escalated"
    ]


# --- exceptions ------------------------------------------------------------

def test_an_active_exception_suppresses_generation(seeded):
    run_cycle(seeded, END_OF_STORY)
    ids = {i.id for i in repositories(seeded)["instances"].list()}
    assert "CHK-THIRD-PARTY-ACCESS-MKTG-2026-Q1" not in ids
    assert "CHK-THIRD-PARTY-ACCESS-MKTG-2026-Q2" not in ids
    assert "CHK-BCP-TEST-PLATFORM-2026" not in ids


def test_the_lapse_returns_the_control_to_the_schedule(seeded):
    """EXC-002 expires 2026-06-30: Q1 and Q2 suppressed, Q3 and Q4 return."""
    run_cycle(seeded, END_OF_STORY)
    ids = {i.id for i in repositories(seeded)["instances"].list()}
    assert "CHK-THIRD-PARTY-ACCESS-MKTG-2026-Q3" in ids
    assert "CHK-THIRD-PARTY-ACCESS-MKTG-2026-Q4" in ids


def test_a_lapsed_exception_raises_its_own_alert(seeded):
    run_cycle(seeded, date(2026, 7, 5))
    events = [
        e
        for e in repositories(seeded)["audit"].read_for("ComplianceException", "EXC-002")
        if e.action == "exception_expired"
    ]
    assert len(events) == 1
    assert events[0].detail["expired_on"] == "2026-06-30"
    assert events[0].detail["detected_on"] == "2026-07-05"
    assert repositories(seeded)["exceptions"].get("EXC-002").status == "expired"


def test_the_lapse_alert_is_routed_to_the_owning_team(seeded):
    result = run_cycle(seeded, date(2026, 7, 5))
    alerts = {
        n.entity_id: n for n in result.notifications if n.kind == "exception_expired"
    }
    # both EXC-002 and EXC-004 have lapsed by this date, each to its own team
    assert set(alerts) == {"EXC-002", "EXC-004"}
    assert alerts["EXC-002"].to_team == "Marketing"
    assert alerts["EXC-004"].to_team == "People Operations"


def test_the_lapse_alert_fires_once_not_every_cycle(seeded):
    for as_of in (date(2026, 7, 5), date(2026, 8, 5), date(2026, 9, 5)):
        run_cycle(seeded, as_of)
    events = [
        e
        for e in repositories(seeded)["audit"].read_for("ComplianceException", "EXC-002")
        if e.action == "exception_expired"
    ]
    assert len(events) == 1


def test_expiring_does_not_retroactively_unsuppress_earlier_periods(seeded):
    """The waiver did apply to Q1 and Q2. Lapsing must not backfill them."""
    run_cycle(seeded, date(2026, 7, 5))   # flips EXC-002 to expired
    run_cycle(seeded, END_OF_STORY)       # would backfill if `covers` looked at status
    ids = {i.id for i in repositories(seeded)["instances"].list()}
    assert "CHK-THIRD-PARTY-ACCESS-MKTG-2026-Q1" not in ids
    assert "CHK-THIRD-PARTY-ACCESS-MKTG-2026-Q2" not in ids


def test_a_revoked_exception_suppresses_nothing(seeded):
    run_cycle(seeded, END_OF_STORY)
    ids = {i.id for i in repositories(seeded)["instances"].list()}
    assert "CHK-INCIDENT-PM-FINREP-2026-03" in ids


def test_covers_ignores_status_flips_but_not_revocation():
    base = dict(
        id="X", control_id="C", process_area_id="A", rationale="r",
        approved_by="b", granted_at=date(2026, 1, 1), expires_at=date(2026, 6, 30),
    )
    inside, outside = date(2026, 3, 31), date(2026, 9, 30)
    for status in ("active", "expired"):
        assert covers(ComplianceException(status=status, **base), "C", "A", inside)
        assert not covers(ComplianceException(status=status, **base), "C", "A", outside)
    assert not covers(ComplianceException(status="revoked", **base), "C", "A", inside)


# --- routing ---------------------------------------------------------------

def test_every_new_instance_is_routed_to_its_owning_team(seeded, corpus):
    result = run_cycle(seeded, END_OF_STORY)
    assigned = [n for n in result.notifications if n.kind == "assigned"]
    teams = {a.id: a.owner_team for a in corpus.areas}
    assert len(assigned) == 343
    for notification in assigned:
        instance = repositories(seeded)["instances"].get(notification.entity_id)
        assert notification.to_team == teams[instance.process_area_id]


def test_notifications_are_logged_and_never_sent(seeded):
    result = run_cycle(seeded, END_OF_STORY)
    logged = [
        e for e in repositories(seeded)["audit"].read_all()
        if e.action == "notification_logged"
    ]
    assert len(logged) == len(result.notifications)
    assert all(e.detail["delivery"] == "logged_not_sent" for e in logged)


def test_no_module_can_send_anything():
    """Section 11: no email. The payload is the integration."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
    forbidden = {"smtplib", "email", "requests", "urllib", "http", "socket"}
    for path in src.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in forbidden, f"{path.name}: {name}"


def test_due_soon_warns_before_the_deadline(seeded):
    result = run_cycle(seeded, date(2026, 8, 10))  # 5 days before 08-15
    due_soon = [
        n for n in result.notifications
        if n.kind == "due_soon" and n.entity_id == "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    ]
    assert len(due_soon) == 1
    assert "due in 5 day(s)" in due_soon[0].subject


def test_notification_kinds_are_all_accounted_for(seeded):
    kinds = set()
    for as_of in (date(2026, 7, 5), date(2026, 8, 10), date(2026, 8, 30),
                  date(2026, 9, 14)):
        kinds |= {n.kind for n in run_cycle(seeded, as_of).notifications}
    assert kinds == {"assigned", "due_soon", "overdue", "escalation",
                     "exception_expired"}


# --- the audit trail -------------------------------------------------------

def test_every_state_change_appends_an_event_with_the_full_shape(seeded):
    run_cycle(seeded, END_OF_STORY)
    for event in repositories(seeded)["audit"].read_all():
        assert isinstance(event.ts, datetime)
        assert event.actor in ("system", "ai", "user")
        assert event.owner and event.action and event.entity_type and event.entity_id
        assert isinstance(event.detail, dict)


def test_the_trail_is_append_only_across_cycles(seeded):
    run_cycle(seeded, date(2026, 6, 1))
    before = repositories(seeded)["audit"].read_all()
    run_cycle(seeded, END_OF_STORY)
    after = repositories(seeded)["audit"].read_all()

    assert len(after) > len(before)
    assert after[: len(before)] == before          # nothing earlier was rewritten
    assert [e.id for e in after] == sorted(e.id for e in after)


def test_the_audit_log_still_refuses_to_mutate():
    from sentinelops.repositories import AuditLog

    assert {n for n in dir(AuditLog) if not n.startswith("_")} == {
        "append", "read_all", "read_for"
    }


def test_a_cycle_records_whether_a_human_started_it(seeded):
    run_cycle(seeded, date(2026, 6, 1), trigger="scheduler", actor="system")
    run_cycle(seeded, date(2026, 7, 1), trigger="manual", actor="user")
    events = [
        e for e in repositories(seeded)["audit"].read_all()
        if e.action == "cycle_started"
    ]
    assert [e.detail["trigger"] for e in events] == ["scheduler", "manual"]
    assert [e.detail["human_triggered"] for e in events] == [False, True]
    assert [e.actor for e in events] == ["system", "user"]


def test_a_cycle_is_bracketed_by_a_start_and_a_completion(seeded):
    run_cycle(seeded, END_OF_STORY)
    actions = [
        e.action for e in repositories(seeded)["audit"].read_all()
        if e.entity_type == "Cycle"
    ]
    assert actions == ["cycle_started", "cycle_completed"]


def test_an_unknown_trigger_is_refused(seeded):
    with pytest.raises(ValueError, match="unknown trigger"):
        run_cycle(seeded, END_OF_STORY, trigger="cron-ish")


def test_one_instance_has_a_reconstructable_timeline(seeded):
    for as_of in (date(2026, 7, 5), date(2026, 8, 20), date(2026, 8, 30),
                  date(2026, 9, 14)):
        run_cycle(seeded, as_of)
    events = repositories(seeded)["audit"].read_for(
        "CheckInstance", "CHK-CUST-COMPLAINTS-CUSTOPS-2026-07"
    )
    actions = [e.action for e in events]
    assert actions[0] == "check_instance_created"
    assert "check_instance_overdue" in actions
    assert actions.count("check_instance_escalated") == 2
    assert [e.ts for e in events] == sorted(e.ts for e in events)


# --- the scheduler is not a second code path -------------------------------

def test_advance_calendar_delegates_to_run_cycle(seeded, monkeypatch):
    import sentinelops.stages.trigger as trigger

    calls = []
    monkeypatch.setattr(
        trigger, "run_cycle",
        lambda conn, as_of, **kw: calls.append((as_of, kw)) or "delegated",
    )
    assert trigger.advance_calendar(seeded, 30, from_date=date(2026, 1, 1)) == "delegated"
    assert calls == [(date(2026, 1, 31), {"trigger": "manual", "actor": "user",
                                          "policy": DEFAULT_POLICY})]


def test_advance_calendar_picks_up_where_the_last_cycle_left_off(seeded):
    run_cycle(seeded, date(2026, 5, 1))
    assert last_cycle_date(seeded) == date(2026, 5, 1)
    result = advance_calendar(seeded, 45)
    assert result.as_of == date(2026, 6, 15)
    assert last_cycle_date(seeded) == date(2026, 6, 15)


def test_advance_calendar_needs_a_starting_point(seeded):
    with pytest.raises(ValueError, match="no prior cycle"):
        advance_calendar(seeded, 30)


# --- zero model calls ------------------------------------------------------

@pytest.fixture()
def exploding_llm(monkeypatch):
    def _no(*args, **kwargs):
        raise AssertionError("S1 must never call a model")

    import sentinelops.llm as llm
    import sentinelops.llm.factory as factory
    from sentinelops.llm.providers.fake import FakeModelClient
    from sentinelops.llm.providers.openai import OpenAIClient

    monkeypatch.setattr(factory, "get_client", _no)
    monkeypatch.setattr(llm, "get_client", _no)
    monkeypatch.setattr(FakeModelClient, "complete", _no)
    monkeypatch.setattr(OpenAIClient, "complete", _no)


def test_a_full_cycle_runs_with_every_provider_rigged_to_explode(seeded, exploding_llm):
    result = run_cycle(seeded, END_OF_STORY)
    assert len(result.created) == 343


def test_a_full_cycle_records_no_token_usage(seeded, exploding_llm):
    run_cycle(seeded, END_OF_STORY)
    assert seeded.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"] == 0


def test_the_trigger_module_cannot_reach_a_model():
    from pathlib import Path

    from test_applicability import _code_only

    src = Path(__file__).resolve().parents[1] / "src" / "sentinelops"
    assert "llm" not in _code_only(src / "stages" / "trigger.py")


# --- the waiver the corpus now reaches on its own --------------------------

def _run_the_year(conn):
    """Advance the calendar month by month, as the demo does.

    A month-end sweep rather than mid-month: a quarterly check due on the 15th
    has then already been marked overdue by the time the next cycle sees it, so
    the waiver lands on an instance that is visibly lapsed rather than merely
    open.
    """
    for month in range(1, 13):
        run_cycle(conn, date(2026, month, 28))
    return run_cycle(conn, END_OF_STORY)


def test_waived_is_reachable_from_the_corpus_alone(seeded):
    """No purpose-built fixture: EXC-004 is part of the seeded data."""
    _run_the_year(seeded)
    waived = [
        i for i in repositories(seeded)["instances"].list() if i.status == "waived"
    ]
    assert [i.id for i in waived] == ["CHK-CRYPTO-KEY-HR-2026-Q1"]


def test_the_waiver_reaches_only_the_obligation_it_names(seeded):
    _run_the_year(seeded)
    repo = repositories(seeded)
    assert repo["instances"].get("CHK-CRYPTO-KEY-HR-2026-Q1").status == "waived"
    for quarter in ("Q2", "Q3", "Q4"):
        instance = repo["instances"].get(f"CHK-CRYPTO-KEY-HR-2026-{quarter}")
        assert instance is not None, "later quarters must still be raised"
        assert instance.status != "waived"


def test_the_waived_instance_was_open_and_overdue_first(seeded):
    """It is a waiver, not a suppression: the check existed and had lapsed."""
    repo = repositories(seeded)
    run_cycle(seeded, date(2026, 4, 15))
    assert repo["instances"].get("CHK-CRYPTO-KEY-HR-2026-Q1").status == "pending"

    run_cycle(seeded, date(2026, 4, 30))
    assert repo["instances"].get("CHK-CRYPTO-KEY-HR-2026-Q1").status == "overdue"

    run_cycle(seeded, date(2026, 5, 15))  # inside EXC-004's window
    assert repo["instances"].get("CHK-CRYPTO-KEY-HR-2026-Q1").status == "waived"


def test_the_waiver_records_who_approved_it(seeded):
    _run_the_year(seeded)
    events = [
        e
        for e in repositories(seeded)["audit"].read_for(
            "CheckInstance", "CHK-CRYPTO-KEY-HR-2026-Q1"
        )
        if e.action == "check_instance_waived"
    ]
    assert len(events) == 1
    detail = events[0].detail
    assert detail["exception_id"] == "EXC-004"
    assert detail["approved_by"] == "Chief Information Security Officer"
    assert detail["from_status"] == "overdue"
    assert detail["was_overdue_by_days"] > 0


def test_the_waiver_is_routed_like_any_other_alert(seeded):
    result = None
    for as_of in (date(2026, 4, 30), date(2026, 5, 15)):
        result = run_cycle(seeded, as_of)
    waivers = [n for n in result.notifications if n.kind == "waived"]
    assert len(waivers) == 1
    assert waivers[0].to_team == "People Operations"
    assert "EXC-004" in waivers[0].subject


def test_a_waived_instance_stays_waived_after_the_exception_lapses(seeded):
    """The obligation was discharged while the waiver held."""
    run_cycle(seeded, date(2026, 5, 15))
    run_cycle(seeded, date(2026, 8, 1))  # EXC-004 expired 2026-06-19
    repo = repositories(seeded)
    assert repo["exceptions"].get("EXC-004").status == "expired"
    assert repo["instances"].get("CHK-CRYPTO-KEY-HR-2026-Q1").status == "waived"


def test_an_expired_waiver_excuses_nothing_new(seeded):
    """A single cycle after the window leaves the check overdue, not waived."""
    run_cycle(seeded, END_OF_STORY)
    instance = repositories(seeded)["instances"].get("CHK-CRYPTO-KEY-HR-2026-Q1")
    assert instance.status == "overdue"


def test_the_fourth_exception_suppresses_no_generation(seeded):
    _run_the_year(seeded)
    ids = {i.id for i in repositories(seeded)["instances"].list()}
    for quarter in ("Q1", "Q2", "Q3", "Q4"):
        assert f"CHK-CRYPTO-KEY-HR-2026-{quarter}" in ids
    assert len(ids) == 343


def test_waives_and_covers_are_complementary():
    """Suppression and waiver must never both claim the same obligation."""
    from sentinelops.stages.trigger import covers, waives

    exception = ComplianceException(
        id="X", control_id="C", process_area_id="A", rationale="r",
        approved_by="b", granted_at=date(2026, 5, 11), expires_at=date(2026, 6, 19),
        status="active",
    )
    q1_end, q2_end = date(2026, 3, 31), date(2026, 6, 30)
    as_of = date(2026, 5, 20)

    assert not covers(exception, "C", "A", q1_end)   # granted after Q1 closed
    assert waives(exception, "C", "A", q1_end, as_of)

    assert not covers(exception, "C", "A", q2_end)   # Q2 outlives the waiver
    assert not waives(exception, "C", "A", q2_end, as_of)

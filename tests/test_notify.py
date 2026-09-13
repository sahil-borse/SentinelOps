"""Notifications as records, and the inbox that falls out of them.

The point of this slice is that a notification can be *asked about*. So the
tests ask: what is waiting for this person, who else was told, and does the
timing match the policy that claims to drive it.
"""

from datetime import date, datetime, timedelta

import pytest

from sentinelops import notify
from sentinelops.directory import load as load_directory
from sentinelops.entities import Finding, Notification
from sentinelops.repositories import repositories, simulated_clock
from sentinelops.stages import followup, rounds
from sentinelops.synth import generate_corpus, seed_database

AS_OF = date(2027, 3, 1)


@pytest.fixture(scope="module")
def corpus():
    return generate_corpus()


@pytest.fixture
def ctx(conn, corpus):
    seed_database(conn, corpus)
    repo = repositories(conn)
    people = load_directory(conn)
    unit = next(u for u in repo["units"].list() if u.id == "AREA-HR")
    auditor = people.by_role("pa_infosec")[0]
    finding = Finding(
        id="FND-NOTIFY-1",
        source="audit",
        auditable_unit_id=unit.id,
        description="Leaver access was not revoked inside the window.",
        raised_by=auditor.id,
        raised_at=datetime(2027, 2, 1, 9, 0),
        owner_identity=unit.owner_identity,
        target_date=date(2027, 2, 8),
        severity="Major",
        severity_assigned_by=auditor.id,
        agreed_action_plan="Revoke and reconcile monthly.",
    )
    with simulated_clock(finding.raised_at):
        repo["findings"].add(finding)
    return conn, repo, people, finding, auditor


# --- the record --------------------------------------------------------------

def test_a_notification_is_a_row_not_a_log_line(ctx):
    conn, repo, people, finding, _ = ctx
    notify.send(
        repo, people, to=finding.owner_identity, kind="reminder",
        subject="A subject", body="A body",
        related_entity=finding.id, as_of=AS_OF,
    )
    # Scoped to this finding: seeding drives the corpus's historical closures
    # through the same path, so the table is not empty when a test starts.
    rows = repo["notifications"].list(related_entity=finding.id)
    assert rows
    note = rows[0]
    assert isinstance(note, Notification)
    assert note.recipient_identity == finding.owner_identity
    assert note.subject and note.body
    assert note.related_entity == finding.id
    assert note.unread and note.read_at is None


def test_every_kind_in_the_spec_is_accepted_and_nothing_else_is(ctx):
    conn, repo, people, finding, _ = ctx
    assert set(notify.KINDS) == {
        "audit_due", "activity_due", "finding_raised", "reminder",
        "evidence_requested", "overdue", "escalation", "evidence_submitted",
        "closure", "exception_lapsed",
    }
    with pytest.raises(ValueError):
        notify.send(
            repo, people, to=finding.owner_identity, kind="shouting",
            subject="s", body="b", related_entity=finding.id, as_of=AS_OF,
        )


def test_the_timestamp_is_simulated_not_the_wall_clock(ctx):
    conn, repo, people, finding, _ = ctx
    notify.send(
        repo, people, to=finding.owner_identity, kind="reminder",
        subject="s", body="b", related_entity=finding.id, as_of=AS_OF,
    )
    note = repo["notifications"].list(related_entity=finding.id)[0]
    assert note.sent_at.date() == AS_OF
    event = [
        e for e in repo["audit"].read_all()
        if e.action == "notification_sent"
        and e.detail["related_entity"] == finding.id
    ][0]
    assert event.ts.date() == AS_OF


def test_nothing_is_actually_sent(ctx):
    """Section 11: no email. The word `send` means `record`, and says so."""
    conn, repo, people, finding, _ = ctx
    notify.send(
        repo, people, to=finding.owner_identity, kind="reminder",
        subject="s", body="b", related_entity=finding.id, as_of=AS_OF,
    )
    event = [
        e for e in repo["audit"].read_all()
        if e.action == "notification_sent"
        and e.detail["related_entity"] == finding.id
    ][0]
    assert event.detail["delivery"] == "recorded_not_sent"

    import ast
    from pathlib import Path
    source = (
        Path(__file__).resolve().parents[1] / "src" / "sentinelops" / "notify.py"
    ).read_text(encoding="utf-8")
    body = source.split('"""', 2)[2]
    for forbidden in ("smtplib", "requests", "urllib", "httpx", "sendmail"):
        assert forbidden not in body, f"notify reaches for {forbidden}"


# --- the inbox ---------------------------------------------------------------

def test_the_inbox_is_per_identity_and_newest_first(ctx):
    conn, repo, people, finding, auditor = ctx
    for day, kind in ((1, "reminder"), (3, "reminder"), (5, "overdue")):
        notify.send(
            repo, people, to=finding.owner_identity, kind=kind,
            subject=f"day {day}", body="b", related_entity=finding.id,
            as_of=AS_OF + timedelta(days=day),
        )
    owner_inbox = [
        n for n in notify.inbox(conn, finding.owner_identity)
        if n.related_entity == finding.id
    ]
    assert [n.subject for n in owner_inbox] == ["day 5", "day 3", "day 1"]

    # the auditor sees only what they were copied on — `overdue`, not the
    # reminders, which are between the system and the owner
    auditor_inbox = [
        n for n in notify.inbox(conn, auditor.id)
        if n.related_entity == finding.id
    ]
    assert {n.kind for n in auditor_inbox} == {"overdue"}


def test_unread_is_per_recipient(ctx):
    conn, repo, people, finding, auditor = ctx
    written = notify.send(
        repo, people, to=finding.owner_identity, kind="overdue",
        subject="s", body="b", related_entity=finding.id, as_of=AS_OF,
    )
    assert len(written) > 1, "the audit team is copied on an overdue"

    def unread_here(identity):
        return len([
            n for n in notify.inbox(conn, identity, unread_only=True)
            if n.related_entity == finding.id
        ])

    assert unread_here(finding.owner_identity) == 1
    assert unread_here(auditor.id) == 1

    notify.mark_read(
        conn, written[0].id, by=finding.owner_identity, as_of=AS_OF
    )
    assert unread_here(finding.owner_identity) == 0
    assert unread_here(auditor.id) == 1, (
        "one reader marking it read must not clear it for another"
    )


def test_only_the_recipient_can_mark_it_read(ctx):
    conn, repo, people, finding, auditor = ctx
    written = notify.send(
        repo, people, to=finding.owner_identity, kind="reminder",
        subject="s", body="b", related_entity=finding.id, as_of=AS_OF,
    )
    with pytest.raises(PermissionError):
        notify.mark_read(conn, written[0].id, by=auditor.id, as_of=AS_OF)


# --- who gets copied ---------------------------------------------------------

def test_pa_infosec_are_copied_on_the_events_they_must_not_miss(ctx):
    """Section 1 has the audit team chasing, reviewing and deciding closure."""
    conn, repo, people, finding, _ = ctx
    auditors = {a.id for a in people.by_role("pa_infosec")}

    for kind in ("finding_raised", "evidence_submitted", "overdue", "closure",
                 "exception_lapsed"):
        written = notify.send(
            repo, people, to=finding.owner_identity, kind=kind,
            subject=kind, body="b", related_entity=finding.id, as_of=AS_OF,
        )
        copied = {n.recipient_identity for n in written} & auditors
        assert copied == auditors, f"{kind} did not reach the audit team"


def test_a_plain_reminder_is_between_the_system_and_the_owner(ctx):
    """Copying the auditors on every nudge would make the copies worthless."""
    conn, repo, people, finding, _ = ctx
    written = notify.send(
        repo, people, to=finding.owner_identity, kind="reminder",
        subject="s", body="b", related_entity=finding.id, as_of=AS_OF,
    )
    assert len(written) == 1
    assert written[0].recipient_identity == finding.owner_identity


def test_an_escalation_is_not_filed_twice_in_one_inbox(ctx):
    """The escalation path addresses the audit team by name, so the automatic
    copy is off. With both, every auditor would get the manager's copy and
    their own, and an inbox that double-files is one people stop reading."""
    conn, repo, people, finding, _ = ctx
    followup.run(conn, date(2027, 2, 20))
    for auditor in people.by_role("pa_infosec"):
        escalations = [
            n for n in notify.inbox(conn, auditor.id)
            if n.kind == "escalation" and n.related_entity == finding.id
        ]
        assert len(escalations) == len({n.subject for n in escalations})


# --- section 5's policy ------------------------------------------------------

def test_the_policy_table_is_printable_and_reads_from_the_constants():
    table = followup.policy_table()
    for severity in followup.SEVERITY_RULES:
        assert severity in table
    for rule in followup.SEVERITY_RULES.values():
        assert f"{rule.target_days}d" in table
    assert str(followup.MAX_DAYS_TO_ESCALATION) in table
    assert "Reminders continue after escalation" in table


def test_no_severity_exceeds_the_stakeholders_one_week_ceiling():
    """Stated preference, asserted rather than trusted."""
    for name, rule in followup.SEVERITY_RULES.items():
        assert rule.escalate_after <= followup.MAX_DAYS_TO_ESCALATION, name


def test_the_notification_history_of_one_finding_is_answerable(ctx):
    conn, repo, people, finding, _ = ctx
    followup.run(conn, date(2027, 2, 10))
    followup.run(conn, date(2027, 2, 14))
    followup.run(conn, date(2027, 2, 20))

    history = notify.history(conn, finding.id)
    assert history
    assert [n.sent_at for n in history] == sorted(n.sent_at for n in history)
    grouped = notify.by_recipient(conn, finding.id)
    assert finding.owner_identity in grouped
    assert any(n.kind == "reminder" for n in grouped[finding.owner_identity])


# --- cost --------------------------------------------------------------------

def test_notifying_never_calls_a_model(ctx, monkeypatch):
    """Section 2 lists reminder and escalation timing under never-AI."""
    conn, repo, people, finding, _ = ctx
    import sentinelops.llm as llm_module

    def explode(*args, **kwargs):
        raise AssertionError("notifications must never call a model")

    monkeypatch.setattr(llm_module, "get_client", explode)
    followup.run(conn, date(2027, 2, 20))
    assert repo["notifications"].list(related_entity=finding.id)
    spent = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    assert spent == 0


def test_the_notify_module_cannot_reach_the_provider_boundary():
    import ast
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[1] / "src" / "sentinelops" / "notify.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        elif isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        for name in names:
            assert "llm" not in name.split("."), f"notify imports {name}"


# --- the deliverable ---------------------------------------------------------

def test_the_inbox_demo_shows_three_reminders_and_one_escalation(capsys):
    """`python -m sentinelops.demo.inbox` is the slide for section 5.

    Run here so it cannot rot. The counts are the point of the demo, so they
    are asserted rather than eyeballed: three chases on one finding, one
    escalation event, and that event landing in three separate inboxes — the
    owner's manager and both auditors.
    """
    from sentinelops.demo import inbox

    inbox.main()
    out = capsys.readouterr().out

    # Each notification is printed twice - once in the flat history, once under
    # the recipient whose inbox it landed in - so count in the history only.
    history = out.split("THE SAME HISTORY")[0]
    assert history.count("  reminder ") == 3, "three reminders, one per cycle"
    assert history.count("  escalation ") == 3, (
        "one escalation event, filed separately for the manager and each auditor"
    )
    assert "escalation L1 -> 3 inboxes" in out
    assert "follow_up_count=3" in out

    # the four recipients, each with their own inbox
    for name in ("D. Ferreira", "M. Castellanos", "P. Kaur", "T. Osei"):
        assert name in out, f"{name} was never told anything"

    # reminders continue past escalation rather than being replaced by it
    assert "4 day(s) overdue" in out

    assert "model calls while chasing: 0" in out
    assert "ok=True" in out

    import re
    stamps = re.findall(r"^\s+(\d{4}-\d{2}-\d{2})", out, re.MULTILINE)
    assert stamps, "the history printed no rows"
    assert all(stamp.startswith("2027-") for stamp in stamps), (
        f"wall-clock timestamps leaked into the notification history: "
        f"{sorted({s for s in stamps if not s.startswith('2027-')})}"
    )


def test_the_inbox_demo_uses_the_shipped_follow_up_engine():
    """A demo that invents its own cadence proves nothing about the product."""
    import ast
    from pathlib import Path as _Path

    source = (
        _Path(__file__).resolve().parents[1]
        / "src" / "sentinelops" / "demo" / "inbox.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.update(alias.name for alias in node.names)
    assert {"followup", "notify"} <= imported, (
        "the demo must drive the real follow-up engine and the real notify module"
    )
    called = {
        node.func.attr for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    for name in ("run", "policy_table", "history", "by_recipient", "mark_read"):
        assert name in called, f"the demo never calls {name}"

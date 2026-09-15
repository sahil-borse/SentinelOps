"""Every section 8 figure, printed for the corpus at "today".

    python -m sentinelops.demo.section_eight

Replays the seeded corpus through every scheduled cycle up to the simulated
today, exactly as the evaluation harness does, then prints the whole portfolio.
The replay spends model calls — classification and recurrence are section 2
uses — and the meter is read either side of the analytics call itself, so the
figure printed at the bottom is what *reporting* cost: nothing.

Nothing here reads the truth file. The planted patterns are checked against it
in `tests/test_section_eight.py`, which lives outside the package for exactly
that reason.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date

from .. import analytics
from ..db import connect
from ..repositories import repositories
from ..stages import intelligence, taxonomy
from ..stages.assess import run as assess
from ..stages.flag import run as flag_stage
from ..stages.followup import run as followup
from ..stages.prescreen import run as prescreen
from ..stages.remediation import reassess_all
from ..stages.trigger import run_cycle
from ..synth import generate_corpus, seed_database
from ..synth.calendar import SIMULATED_TODAY

#: The harness's cycle dates: the 28th of every month up to today, then today.
CYCLES = [
    d for d in (
        [date(2026, month, 28) for month in range(1, 13)]
        + [date(2027, month, 28) for month in range(1, 13)]
    )
    if d <= SIMULATED_TODAY
] + [SIMULATED_TODAY]


def replay(conn) -> None:
    """Seed, run every cycle to today, then classify and detect recurrence."""
    seed_database(conn, generate_corpus())
    for as_of in CYCLES:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        followup(conn, as_of)
        reassess_all(conn, as_of)
    taxonomy.derive(conn, SIMULATED_TODAY)
    intelligence.classify(conn, SIMULATED_TODAY)
    intelligence.detect_recurrence(conn, SIMULATED_TODAY)


def _rule(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def _pct(value: float) -> str:
    return f"{value:5.1f}%"


def _days(value) -> str:
    """One decimal place always. `statistics.mean` hands back an int when the
    mean happens to be whole, and a column reading 31 beside 30.0 looks like two
    different kinds of number."""
    return "-" if value is None else f"{value:.1f}"


def _counts(title: str, counts: dict[str, int], width: int = 34) -> None:
    total = sum(counts.values())
    print(f"  {title}")
    for name, count in counts.items():
        share = 100 * count / total if total else 0.0
        print(f"    {name.replace('_', ' '):<{width}} {count:>4}  {_pct(share)}")


def _recurring_table(block: dict, label: str) -> None:
    print(f"  {label}: {block['count']} recurring categor"
          f"{'y' if block['count'] == 1 else 'ies'}, "
          f"{block['findings_involved']} findings, "
          f"{block['spanning_units']} across units, "
          f"{block['spanning_periods']} across periods")
    if not block["categories"]:
        return
    print(f"    {'category':<31} {'findings':>8} {'units':>5} {'quarters':>8} "
          f"{'span':>6}  first -> last")
    for name, row in block["categories"].items():
        print(f"    {name.replace('_', ' '):<31} {row['findings']:>8} "
              f"{row['units']:>5} {len(row['periods']):>8} "
              f"{row['months_spanned']:>4}mo  "
              f"{row['first_raised']} -> {row['last_raised']}")


def main() -> None:
    conn = connect(":memory:")
    replay(conn)
    repo = repositories(conn)

    before = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]
    p = analytics.portfolio(conn, SIMULATED_TODAY)
    after = conn.execute("SELECT COUNT(*) c FROM token_usage").fetchone()["c"]

    start, end = p["window"]
    print(f"SECTION 8 - PORTFOLIO AT {SIMULATED_TODAY}  "
          f"(window {start} to {end}, {len(CYCLES)} cycles replayed)")

    # 1 ------------------------------------------------------------------------
    _rule("1. OPEN VS CLOSED - COUNT AND PERCENTAGE, OVERALL AND PER UNIT")
    ovc = p["open_vs_closed"]
    print(f"  overall  {ovc['total']} findings: {ovc['open']} open "
          f"({ovc['open_pct']}%), {ovc['closed']} closed ({ovc['closed_pct']}%)")
    print(f"    {'unit':<24} {'open':>5} {'closed':>7} {'total':>6} "
          f"{'open %':>7} {'closed %':>9}")
    for unit, row in ovc["by_unit"].items():
        print(f"    {unit:<24} {row['open']:>5} {row['closed']:>7} "
              f"{row['total']:>6} {_pct(row['open_pct']):>7} "
              f"{_pct(row['closed_pct']):>9}")

    # 2 ------------------------------------------------------------------------
    _rule("2. SEVERITY MIX - PER UNIT")
    mix = p["severity_mix"]
    print(f"    {'unit':<24} {'Major':>6} {'Minor':>6} {'Observation':>12}")
    for unit, row in mix["by_unit"].items():
        print(f"    {unit:<24} {row['Major']:>6} {row['Minor']:>6} "
              f"{row['Observation']:>12}")
    overall = mix["overall"]
    print(f"    {'all units':<24} {overall['Major']:>6} {overall['Minor']:>6} "
          f"{overall['Observation']:>12}")

    # 3 ------------------------------------------------------------------------
    _rule("3. OVERDUE, AGED - DAYS PAST TARGET")
    ageing = p["overdue_ageing"]
    print(f"  {ageing['total']} open findings past target; oldest "
          f"{ageing['oldest_days']} days")
    for bucket, count in ageing["buckets"].items():
        ids = ageing["findings"][bucket]
        shown = ", ".join(ids[:4]) + (f" +{len(ids) - 4} more" if len(ids) > 4 else "")
        print(f"    {bucket:>6} days  {count:>3}  {shown}")

    # 4 ------------------------------------------------------------------------
    _rule("4. FINDINGS BY UNIT, BY GAP CATEGORY, BY AUDIT KIND")
    dims = p["by_dimension"]
    _counts("by unit", dims["by_unit"])
    _counts("by gap category", dims["by_category"])
    _counts("by audit kind", dims["by_audit_kind"])

    # 5 ------------------------------------------------------------------------
    _rule("5. RECURRING - SAME GAP CATEGORY, DIFFERENT UNIT OR PERIOD")
    rec = p["recurring"]
    _recurring_table(rec["audit_track"], "audit track (auditors' own words)")
    print()
    _recurring_table(rec["by_gap_category"], "all findings")
    print(f"\n  beside it, not instead of it: the recurrence detector asserted "
          f"{rec['count']} links across {rec['findings_involved']} findings, "
          f"{rec['spanning_units']} between different units")
    for chain in rec["longest_chains"][:3]:
        print(f"    {(chain['category'] or '?').replace('_', ' ')}: "
              f"{' -> '.join(chain['findings'])} "
              f"({', '.join(chain['units'])}, {chain['months_spanned']} months)")

    # 6 ------------------------------------------------------------------------
    _rule("6. MULTIPLE EVIDENCE ROUNDS OR MULTIPLE REMINDERS - DISTRIBUTIONS")
    effort = p["effort"]
    print(f"    {'per finding':<12} {'evidence rounds':>16} {'reminders':>10}")
    keys = sorted(set(effort["rounds"]) | set(effort["reminders"]),
                  key=lambda k: (k == "5+", k))
    for key in keys:
        print(f"    {key:<12} {effort['rounds'].get(key, 0):>16} "
              f"{effort['reminders'].get(key, 0):>10}")
    print(f"  {effort['multi_round']} findings needed more than one round "
          f"(most: {effort['worst_rounds']}); {effort['multi_reminder']} needed "
          f"more than one reminder (most: {effort['worst_reminders']})")
    print(f"  three or more rounds: "
          f"{', '.join(effort['three_plus_round_findings']) or 'none'}")

    # 7 ------------------------------------------------------------------------
    _rule("7. OPEN FINDINGS BY MONTH - AND WHICH WAY IT IS GOING")
    peak = max((pt["open"] for pt in p["trend"]), default=0) or 1
    for point in p["trend"]:
        bar = "#" * round(40 * point["open"] / peak)
        year, month = (int(part) for part in point["month"].split("-"))
        month_end = date(year, month, monthrange(year, month)[1]).isoformat()
        cut = "" if point["as_of"] == month_end else f"  (to {point['as_of']})"
        print(f"    {point['month']}  {point['open']:>3}  {bar}{cut}")
    verdict = p["trend_verdict"]
    print(f"\n  across the window: {verdict['direction'].upper()} "
          f"({verdict['slope_per_month']:+.2f} open findings a month; "
          f"{verdict['first']['month']} {verdict['first']['open']} -> "
          f"{verdict['last']['month']} {verdict['last']['open']}, peak "
          f"{verdict['peak']['open']} in {verdict['peak']['month']})")
    recent = verdict["recent"]
    if "change" in recent:
        print(f"  last quarter:      {recent['direction'].upper()} "
              f"(mean {recent['last_quarter_mean']} against "
              f"{recent['previous_quarter_mean']} the quarter before, "
              f"{recent['change']:+.1f})")
    print(f"  rule: {verdict['rule']}; recent: {recent['rule']}")

    # 8 ------------------------------------------------------------------------
    _rule("8. CLOSURE PERFORMANCE - DAYS FROM RAISE TO CLOSURE, BY SEVERITY")
    print(f"    {'severity':<12} {'closed':>6} {'mean':>6} {'median':>7} {'slowest':>8}")
    for severity, row in p["closure"].items():
        print(f"    {severity:<12} {row['closed']:>6} {_days(row['mean_days']):>6} "
              f"{_days(row['median_days']):>7} {str(row['slowest_days']):>8}")

    # 9 ------------------------------------------------------------------------
    _rule(f"9. DUE IN THE NEXT {p['upcoming']['horizon_days']} DAYS")
    up = p["upcoming"]
    print(f"  audits: {len(up['audits'])}")
    for audit in up["audits"]:
        print(f"    {audit['planned']}  in {audit['days_away']:>2} days  {audit['id']}  "
              f"{audit['kind'].replace('_', ' ')}  ({', '.join(audit['scope'])})")
    print(f"  compliance activities: {up['activity_total']}")
    for activity in up["activities"][:10]:
        print(f"    {activity['due']}  in {activity['days_away']:>2} days  "
              f"{activity['control']} - {activity['unit']} {activity['period']}")
    instances = repo["instances"].list()
    if instances:
        latest = max(i.due_date for i in instances)
        print(f"  latest due date of any scheduled activity: {latest}")

    # cost -----------------------------------------------------------------------
    _rule("COST")
    print(f"  model calls during the analytics: {after - before}")
    print(f"  model calls during the replay that produced the state: {before}")
    print(f"  {repo['audit'].verify_chain()}")
    conn.close()


if __name__ == "__main__":
    main()

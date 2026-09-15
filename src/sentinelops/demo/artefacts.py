"""The two generated artefacts, and what one cycle costs.

    python -m sentinelops.demo.artefacts

Replays the corpus to the cycle before "today", then runs today's cycle on its
own with the token meter marked either side, so the cost printed is one cycle's
and not the history's. The prioritisation brief is part of that cycle. The audit
report is generated for the most recent completed audit, confirmed by its
auditor, and issued.

Both artefacts are written as markdown and as self-contained HTML.

**On the token figures.** They are read off the response objects, as section 9
requires, but the responses come from `FakeModelClient`, whose counts are
proportional to the prompt it was handed rather than produced by a real
tokenizer, and whose cost uses the placeholder rates in `llm/metering.py`. Treat
the shape — which call spends what share — as the durable figure, and re-run
against the real provider before quoting dollars.
"""

from __future__ import annotations

from pathlib import Path

from .. import priority, render
from ..db import connect
from ..directory import load as load_directory
from ..repositories import repositories
from ..stages import audits, intelligence, taxonomy
from ..stages.assess import run as assess
from ..stages.flag import run as flag_stage
from ..stages.followup import run as followup
from ..stages.prescreen import run as prescreen
from ..stages.remediation import reassess_all
from ..stages.trigger import run_cycle
from ..synth import generate_corpus, seed_database
from .section_eight import CYCLES

OUT = Path(__file__).resolve().parents[3] / "data" / "artefacts"


def _rule(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def _cycle(conn, as_of) -> None:
    run_cycle(conn, as_of)
    screen = prescreen(conn, as_of)
    if screen.to_assess:
        assess(conn, screen.to_assess, as_of)
    flag_stage(conn, as_of)
    followup(conn, as_of)
    reassess_all(conn, as_of)


def _mark(conn) -> int:
    return conn.execute("SELECT COALESCE(MAX(id), 0) m FROM token_usage").fetchone()["m"]


def _spend(conn, after: int) -> list[dict]:
    """Model calls after a mark, grouped by what made them."""
    groups: dict[str, dict] = {}
    for row in conn.execute(
        "SELECT label, input_tokens, output_tokens, cached_tokens, cost_usd "
        "FROM token_usage WHERE id > ? ORDER BY id", (after,)
    ):
        name = (row["label"] or "unlabelled").split(":", 1)[0]
        group = groups.setdefault(name, {
            "what": name, "calls": 0, "input": 0, "output": 0, "cached": 0, "cost": 0.0,
        })
        group["calls"] += 1
        group["input"] += row["input_tokens"]
        group["output"] += row["output_tokens"]
        group["cached"] += row["cached_tokens"]
        group["cost"] += row["cost_usd"]
    return sorted(groups.values(), key=lambda g: -(g["input"] + g["output"]))


def _print_spend(rows: list[dict]) -> None:
    print(f"    {'what':<10} {'calls':>6} {'input':>9} {'output':>8} {'cached':>8} "
          f"{'total':>9} {'cost USD':>10}")
    for row in rows:
        print(f"    {row['what']:<10} {row['calls']:>6} {row['input']:>9,} "
              f"{row['output']:>8,} {row['cached']:>8,} "
              f"{row['input'] + row['output']:>9,} {row['cost']:>10.4f}")
    total = {k: sum(r[k] for r in rows) for k in ("calls", "input", "output", "cached", "cost")}
    print(f"    {'total':<10} {total['calls']:>6} {total['input']:>9,} "
          f"{total['output']:>8,} {total['cached']:>8,} "
          f"{total['input'] + total['output']:>9,} {total['cost']:>10.4f}")


def main(out_dir: Path | None = None) -> None:
    out = Path(out_dir or OUT)
    out.mkdir(parents=True, exist_ok=True)

    conn = connect(":memory:")
    seed_database(conn, generate_corpus())
    history, today = CYCLES[:-1], CYCLES[-1]
    for as_of in history:
        _cycle(conn, as_of)
    last = history[-1]
    taxonomy.derive(conn, last)
    intelligence.classify(conn, last)
    intelligence.detect_recurrence(conn, last)
    repo = repositories(conn)

    # --- one cycle, metered on its own --------------------------------------
    mark = _mark(conn)
    _cycle(conn, today)
    intelligence.classify(conn, today)
    intelligence.detect_recurrence(conn, today)
    brief = intelligence.prioritisation_brief(conn, today)
    cycle_spend = _spend(conn, mark)

    print(f"ARTEFACTS AT {today}  ({len(history)} cycles replayed, then today's on its own)")

    _rule("PRIORITY ORDER - HOW THE RANKING IS BUILT")
    print(priority.formula_table())

    _rule(f"RANKED OPEN FINDINGS AT {today} (top 10 of {len(brief.ranked)})")
    for row in brief.ranked[:10]:
        print(f"  {row['rank']:>2}. {row['id']:<40} {row['unit']:<12} "
              f"{row['band']:<12} {'chronic' if row['chronic'] else '':<8} "
              f"{row['score']:>4g} pts")
        print(f"      {row['explain']}")

    _rule("PRIORITISATION BRIEF")
    print(f"  brief: {'published' if brief.published else 'WITHHELD'} - "
          f"{len(brief.cited_findings)} finding(s) and {len(brief.cited_metrics)} "
          f"metric(s) cited")
    print()
    print(render.brief_markdown(brief))
    brief_name = f"prioritisation_brief_{today}"
    (out / f"{brief_name}.md").write_text(render.brief_markdown(brief), encoding="utf-8")
    (out / f"{brief_name}.html").write_text(render.brief_html(brief), encoding="utf-8")

    # --- the audit report ---------------------------------------------------
    audit = max(
        (a for a in repo["audits"].list()
         if a.status == "completed" and audits.findings_of(repo, a.id)),
        key=lambda a: (a.conducted_date, a.id),
    )
    report_mark = _mark(conn)
    report = audits.generate_report(conn, audit.id, as_of=today)
    report_spend = _spend(conn, report_mark)
    audits.confirm(conn, audit.id, by=audit.auditor_identity, as_of=today,
                   remarks="Read against the findings; summary citations checked.")
    audits.issue(conn, audit.id, by=audit.auditor_identity, as_of=today)
    audits.attach_status(conn, report)

    _rule(f"AUDIT REPORT - {audit.id}")
    print(f"  report status: {audits.report_status(report)}")
    trail = [e.action for e in repo["audit"].read_for("ScheduledAudit", audit.id)]
    print(f"  trail: {' -> '.join(trail)}")
    print()
    markdown = audits.render_markdown(report)
    print(markdown)
    report_name = f"audit_report_{audit.id}"
    (out / f"{report_name}.md").write_text(markdown, encoding="utf-8")
    (out / f"{report_name}.html").write_text(render.report_html(report), encoding="utf-8")

    # --- cost ---------------------------------------------------------------
    _rule(f"TOKEN COST OF ONE CYCLE ({today})")
    _print_spend(cycle_spend)
    brief_row = next((r for r in cycle_spend if r["what"] == "BRIEF"), None)
    if brief_row:
        cycle_tokens = sum(r["input"] + r["output"] for r in cycle_spend)
        print(f"\n  the brief is {brief_row['calls']} call and "
              f"{brief_row['input'] + brief_row['output']:,} of the cycle's "
              f"{cycle_tokens:,} tokens")

    _rule("TOKEN COST OF THE AUDIT REPORT")
    _print_spend(report_spend)
    print("\n  token counts are read off the response objects, but these responses"
          "\n  come from FakeModelClient: counts proportional to the prompt, priced"
          "\n  at placeholder rates. Re-run on the real provider before quoting cost.")

    _rule("WRITTEN")
    for path in sorted(out.glob("*")):
        if path.name.startswith((brief_name, report_name)):
            print(f"  {path}")
    print(f"\n  {repo['audit'].verify_chain()}")
    conn.close()


if __name__ == "__main__":
    main()

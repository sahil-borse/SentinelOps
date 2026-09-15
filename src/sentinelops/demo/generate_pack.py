"""Produce an audit evidence pack for the corpus window, up to today.

    python -m sentinelops.demo.generate_pack

Runs the whole pipeline over the seeded corpus, then builds the pack from the
audit log alone and writes both renderings.

The period used to be written in as "calendar year 2026" while the replay ran
into March 2027, so the pack's own cover disagreed with the events inside it.
Both now come from the corpus window and the vantage point.
"""

from __future__ import annotations

from pathlib import Path

from ..db import connect
from ..pack import build, load_events, pack_filename, render_html, render_markdown
from ..periods import monthly_cycles
from ..stages.assess import run as assess
from ..stages.flag import run as flag_stage
from ..stages.followup import run as followup
from ..stages.prescreen import run as prescreen
from ..stages.remediation import reassess_all
from ..stages.trigger import run_cycle
from ..synth import generate_corpus, seed_database
from ..synth.calendar import CORPUS_WINDOW, SIMULATED_TODAY

OUT = Path(__file__).resolve().parents[3] / "data" / "packs"
CYCLES = monthly_cycles(CORPUS_WINDOW, SIMULATED_TODAY) + [SIMULATED_TODAY]
PERIOD_START = CORPUS_WINDOW.start
PERIOD_END = SIMULATED_TODAY


def main() -> None:
    conn = connect(":memory:")
    seed_database(conn, generate_corpus())
    for as_of in CYCLES:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        followup(conn, as_of)
        reassess_all(conn, as_of)

    events = load_events(conn, since=PERIOD_START, until=PERIOD_END)
    pack = build(
        events,
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        scope=(
            f"All auditable units, all applicable controls, "
            f"{PERIOD_START} to {PERIOD_END}"
        ),
    )
    OUT.mkdir(parents=True, exist_ok=True)
    name = pack_filename(PERIOD_START, PERIOD_END)
    (OUT / f"{name}.md").write_text(render_markdown(pack), encoding="utf-8")
    (OUT / f"{name}.html").write_text(render_html(pack), encoding="utf-8")

    print(f"events replayed        {pack.totals['events']:,}")
    print(f"chain                  {'VERIFIED' if pack.chain['ok'] else 'FAILED'}")
    for key in ("units", "controls", "due", "completed", "waived", "unexamined",
                "assessments", "superseded_findings", "non_compliant", "human_review",
                "decided_without_a_model", "exceptions", "actions",
                "actions_resolved"):
        print(f"{key:<22} {pack.totals[key]:,}")
    if pack.unknown_actions:
        print(f"UNRECOGNISED ACTIONS   {pack.unknown_actions}")
    print(f"\nwritten: {OUT / (name + '.html')}")
    print(f"         {OUT / (name + '.md')}")


if __name__ == "__main__":
    main()

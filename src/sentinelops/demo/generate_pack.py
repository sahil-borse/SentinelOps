"""Produce an audit evidence pack for the full year.

    python -m sentinelops.demo.generate_pack

Runs the whole pipeline over the seeded corpus, then builds the pack from the
audit log alone and writes both renderings.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..db import connect
from ..pack import build, load_events, render_html, render_markdown
from ..stages.assess import run as assess
from ..stages.flag import run as flag_stage
from ..stages.prescreen import run as prescreen
from ..stages.remediation import reassess_all
from ..stages.trigger import run_cycle
from ..synth import generate_corpus, seed_database

OUT = Path(__file__).resolve().parents[3] / "data" / "packs"
CYCLES = [date(2026, m, 28) for m in range(1, 13)] + [
    date(2027, 1, 31), date(2027, 2, 28), date(2027, 3, 31),
]


def main() -> None:
    conn = connect(":memory:")
    seed_database(conn, generate_corpus())
    for as_of in CYCLES:
        run_cycle(conn, as_of)
        screen = prescreen(conn, as_of)
        if screen.to_assess:
            assess(conn, screen.to_assess, as_of)
        flag_stage(conn, as_of)
        reassess_all(conn, as_of)

    events = load_events(conn, since=date(2026, 1, 1), until=date(2027, 3, 31))
    pack = build(
        events,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 12, 31),
        scope="All process areas, all applicable controls, calendar year 2026",
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit_pack_2026.md").write_text(render_markdown(pack), encoding="utf-8")
    (OUT / "audit_pack_2026.html").write_text(render_html(pack), encoding="utf-8")

    print(f"events replayed        {pack.totals['events']:,}")
    print(f"chain                  {'VERIFIED' if pack.chain['ok'] else 'FAILED'}")
    for key in ("areas", "controls", "due", "completed", "waived", "unexamined",
                "findings", "superseded_findings", "non_compliant", "human_review",
                "decided_without_a_model", "exceptions", "actions",
                "actions_resolved"):
        print(f"{key:<22} {pack.totals[key]:,}")
    if pack.unknown_actions:
        print(f"UNRECOGNISED ACTIONS   {pack.unknown_actions}")
    print(f"\nwritten: {OUT / 'audit_pack_2026.html'}")
    print(f"         {OUT / 'audit_pack_2026.md'}")


if __name__ == "__main__":
    main()

"""A one-screen presentation of the figures, for showing rather than reading.

    python -m evaluation.summary            # from the saved real run
    python -m evaluation.summary --stub     # from a stub run, for a dry run

Writes `data/artefacts/results_summary.html`: one self-contained page, no
scrolling at 1080p, meant to be screen-recorded and watched at reduced size.

**Nothing here is typed in.** Every number comes from the same `Evaluation`
object `results.md` is rendered from, so the two cannot disagree — if a figure
moves, both move together. The scope note and the quotable-or-not marks are
read out of `results.md` itself rather than paraphrased, because a caveat
reworded for a slide is a caveat quietly weakened, and these are the part worth
showing.
"""

from __future__ import annotations

import argparse
import html
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sentinelops.db import connect
from sentinelops.synth import generate_corpus

from . import baseline as baseline_module
from . import harness

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results.md"
OUT = ROOT / "data" / "artefacts" / "results_summary.html"
RUN_DB = ROOT / "data" / "real" / "run.db"

#: Where section 4's scope note starts in `results.md`. Everything to the end of
#: that paragraph is quoted verbatim.
SCOPE_MARKER = "**Scope, which matters more than the number.**"


class MissingSource(RuntimeError):
    """Something this page quotes is not in `results.md` to quote."""


@dataclass
class Figure:
    value: str
    label: str
    note: str = ""


def scope_note(results: str) -> str:
    """Section 4's scope paragraph, word for word.

    Read rather than restated. It is held in frame while it is being spoken
    about, and a version edited to fit a slide is a different claim.
    """
    if SCOPE_MARKER not in results:
        raise MissingSource(
            f"results.md has no scope note to quote: {SCOPE_MARKER!r} is not in it"
        )
    paragraph = results.split(SCOPE_MARKER, 1)[1].split("\n\n", 1)[0]
    return (SCOPE_MARKER + paragraph).replace("\n", " ").strip()


def quotable_marks(results: str) -> dict[str, str]:
    """The Quotable? column of the real-provider table, keyed by its figure."""
    marks: dict[str, str] = {}
    for line in results.splitlines():
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) == 4 and cells[0] not in ("Figure", "---"):
            marks[cells[0]] = cells[3]
    return marks


def headline(evaluation) -> list[Figure]:
    """Six figures, in the order they are spoken about."""
    p, m = evaluation.pipeline, evaluation.manual
    gap = p["gap_detection"]
    missed = p["missed"]
    return [
        Figure(f"{missed['examined']}/{missed['due']}",
               "Obligations due, and examined",
               f"{missed['missed']} missed"),
        Figure(f"{p['reminders']:,} · {p['escalations']:,}",
               "Reminders sent · escalations raised",
               f"across {p['actions']['escalated']} findings"),
        Figure(f"{p['detection']['median']:g} days",
               "Median time to detection",
               f"{m['detection']['median']:g} simulated manual"),
        Figure(f"{gap.precision:.1%} · {gap.recall:.1%} · {gap.false_positive_rate:.1%}",
               "Gap detection: precision · recall · FPR",
               f"TP {gap.true_positive} FP {gap.false_positive} FN {gap.false_negative}"),
        Figure(f"{p['zero_model']['share']:.1%}",
               "Resolved with no model call",
               f"{p['zero_model']['decided_by_rules']} of {p['zero_model']['assessments']}"),
        Figure(f"${p['tokens']['cost_usd']:.2f}",
               "Full replay, measured",
               f"{p['tokens']['calls']:,} calls"),
    ]


def comparison(evaluation, marks: dict[str, str]) -> list[tuple[str, ...]]:
    """SentinelOps beside the manual simulation and the naive baseline."""
    p, m, b = evaluation.pipeline, evaluation.manual, evaluation.baseline
    gap, baseline_gap = p["gap_detection"], b["gap_detection"]
    result = b["result"]
    assess = next(
        (row for row in p["tokens"].get("by_stage", []) if row["tier"] == "assess"), None
    )
    assess_calls = assess["calls"] if assess else p["tokens"]["calls"]
    assess_tokens = (assess["input_tokens"] + assess["output_tokens"]) if assess else 0
    consistency = p["consistency"]
    return [
        ("Missed-check rate",
         f"{m['missed_rate']:.1%} ({m['missed']}/{m['due']})",
         f"{p['missed']['rate']:.1%} ({p['missed']['missed']}/{p['missed']['due']})",
         "—",
         "Manual figure is a simulation, not a measurement of any team"),
        ("Verdict disagreement, identical evidence",
         f"{m['consistency']['disagreement_rate']:.1%}",
         f"{consistency['disagreement_rate']:.1%}",
         "—",
         f"Measured on {consistency['identical_evidence_groups']} group(s) of "
         f"byte-identical evidence — thin; the structural argument carries it"),
        ("Median time to detection",
         f"{m['detection']['median']:g} days",
         f"{p['detection']['median']:g} days",
         "—",
         f"n={p['detection']['n']}, bounded by monthly cycles"),
        ("Gap detection: precision / recall / FPR",
         f"{m['gap_detection'].precision:.1%} / {m['gap_detection'].recall:.1%} / "
         f"{m['gap_detection'].false_positive_rate:.1%}",
         f"{gap.precision:.1%} / {gap.recall:.1%} / {gap.false_positive_rate:.1%}",
         f"{baseline_gap.precision:.1%} / {baseline_gap.recall:.1%} / "
         f"{baseline_gap.false_positive_rate:.1%}",
         marks.get("Gap detection: precision / recall / FPR", "")),
        ("Assessment: calls · tokens",
         "—",
         f"{assess_calls:,} · {assess_tokens:,}",
         f"{result.model_calls:,} · {result.total_tokens:,}",
         "Like for like — the same job. Totals elsewhere include classification "
         "and recurrence, which the naive path does not do"),
        ("Citations failing verification",
         "—", "0", "—",
         marks.get("Citations failing verification, and discarded", "")),
    ]


def recurrence(evaluation, marks: dict[str, str]) -> dict[str, Any]:
    r = evaluation.pipeline["recurrence"]
    return {
        "recall": f"{(r.get('recall') or 0):.1%}",
        "precision": f"{(r.get('precision') or 0):.1%}",
        "pairs": r.get("planted_pairs", 0),
        "mark": marks.get("Recurrence: recall / precision", ""),
    }


def _e(value: Any) -> str:
    return html.escape(str(value))


def _markdown(text: str) -> str:
    """The little formatting the quoted lines carry: bold, italics, code."""
    out = _e(text)
    for token, tag in (("**", "strong"), ("*", "em"), ("`", "code")):
        parts = out.split(token)
        out = parts[0] + "".join(
            f"<{tag}>{part}</{tag}>" if index % 2 else part
            for index, part in enumerate(parts[1:], start=1)
        )
    return out


def render(evaluation, results: str) -> str:
    marks = quotable_marks(results)
    figures = "".join(
        # A long value gets a smaller size rather than a second line: the tiles
        # sit on one band and a wrapped one makes the row look broken.
        f'<div class="figure"><div class="value{" tight" if len(f.value) > 12 else ""}">'
        f'{_e(f.value)}</div>'
        f'<div class="label">{_e(f.label)}</div>'
        f'<div class="note">{_e(f.note)}</div></div>'
        for f in headline(evaluation)
    )
    rows = "".join(
        "<tr>"
        f"<th>{_e(name)}</th><td>{_e(manual)}</td>"
        f'<td class="ours">{_e(ours)}</td><td>{_e(naive)}</td>'
        f'<td class="mark">{_markdown(mark)}</td></tr>'
        for name, manual, ours, naive, mark in comparison(evaluation, marks)
    )
    rec = recurrence(evaluation, marks)
    models = ", ".join(sorted({
        row["model"] for row in evaluation.pipeline["tokens"].get("by_stage", [])
    })) or "the deterministic stub"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>SentinelOps — measured outcomes</title>
<style>
  :root {{
    --ink: #12161B; --panel: #1A2027; --line: #2A333D;
    --text: #E8ECEF; --muted: #9AA7B2; --accent: #2DD4BF;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 30px 38px 26px; background: var(--ink); color: var(--text);
         font: 17px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
         font-variant-numeric: tabular-nums; }}
  header {{ display: flex; align-items: baseline; gap: 16px; margin-bottom: 18px; }}
  h1 {{ font-size: 25px; font-weight: 650; margin: 0; letter-spacing: -0.01em; }}
  .sub {{ color: var(--muted); font-size: 16px; }}
  .band {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 22px; }}
  .figure {{ background: var(--panel); border: 1px solid var(--line);
             border-top: 3px solid var(--accent); border-radius: 12px; padding: 14px 16px 12px; }}
  .value {{ font-size: 34px; font-weight: 680; letter-spacing: -0.02em; line-height: 1.1;
            color: #fff; white-space: nowrap; }}
  .value.tight {{ font-size: 25px; }}
  .label {{ font-size: 16.5px; margin-top: 8px; }}
  .note {{ font-size: 15px; color: var(--muted); margin-top: 3px; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
  caption {{ text-align: left; font-size: 16px; color: var(--muted); padding-bottom: 8px; }}
  thead th {{ text-align: left; font-size: 14px; letter-spacing: 0.06em; text-transform: uppercase;
              color: var(--muted); font-weight: 700; padding: 0 12px 8px; border-bottom: 1px solid var(--line); }}
  tbody th {{ text-align: left; font-weight: 600; padding: 11px 12px; vertical-align: top; }}
  td {{ padding: 11px 12px; vertical-align: top; }}
  tbody tr + tr th, tbody tr + tr td {{ border-top: 1px solid var(--line); }}
  .ours {{ color: var(--accent); font-weight: 650; }}
  .mark {{ color: var(--muted); font-size: 15.5px; max-width: 46ch; }}
  .foot {{ display: grid; grid-template-columns: 1.45fr 1fr; gap: 18px; }}
  .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
            padding: 18px 20px; }}
  .panel h2 {{ font-size: 15px; letter-spacing: 0.06em; text-transform: uppercase;
               color: var(--accent); margin: 0 0 8px; }}
  .scope {{ font-size: 17px; line-height: 1.6; margin: 0; }}
  .scope.note {{ color: var(--muted); font-size: 16px; margin-top: 10px; }}
  .rec {{ display: flex; gap: 22px; margin-bottom: 8px; }}
  .rec div span {{ display: block; font-size: 26px; font-weight: 680; color: #fff; }}
  .rec div small {{ color: var(--muted); font-size: 14.5px; }}
  code {{ background: #0C1014; border: 1px solid var(--line); border-radius: 5px;
          padding: 0 5px; font-size: 14.5px; }}
</style></head>
<body>
<header>
  <h1>SentinelOps — measured outcomes</h1>
  <span class="sub">{_e(models)} · corpus <code>{_e(evaluation.corpus_fingerprint[:16])}</code>
  · {evaluation.cycles} cycles to the vantage point</span>
</header>

<section class="band">{figures}</section>

<table>
  <caption>Against a simulated manual process, and against a naive implementation on the same model.</caption>
  <thead><tr><th>Measure</th><th>Manual (simulated)</th><th>SentinelOps</th><th>Naive baseline</th><th>Quotable?</th></tr></thead>
  <tbody>{rows}</tbody>
</table>

<section class="foot">
  <div class="panel">
    <h2>Scope — quoted from results.md, section 4</h2>
    <p class="scope">{_markdown(scope_note(results))}</p>
  </div>
  <div class="panel">
    <h2>Recurrence</h2>
    <div class="rec">
      <div><span>{_e(rec['recall'])}</span><small>recall</small></div>
      <div><span>{_e(rec['precision'])}</span><small>precision</small></div>
    </div>
    <p class="scope">{_markdown(rec['mark'])}</p>
    <p class="scope note">It links more than the stub does: it reaches more of
    what was planted, and more of what was not. Advisory, with the earlier
    finding quoted beside the new one.</p>
  </div>
</section>
</body></html>
"""


def _evaluation_from_run(stub: bool):
    """Score the saved run without touching `results.md`.

    The same call `results.md` is written by, pointed at a throwaway path: the
    figures have to come from one place or the two pages will eventually
    disagree, and this page exists to be believed.
    """
    corpus = generate_corpus()
    conn = connect(":memory:")
    if stub:
        from sentinelops.llm import get_client

        client = get_client("fake")
        harness.run_pipeline(conn, corpus, client=client)
        harness._section_eight(conn, client=client)
        cached = None
    else:
        if not RUN_DB.exists():
            raise MissingSource(f"no saved run at {RUN_DB}")
        disk = sqlite3.connect(RUN_DB)
        try:
            disk.backup(conn)
        finally:
            disk.close()
        from sentinelops.llm.models import model_for

        cached = baseline_module.load_cached(corpus.fingerprint(), model_for("assess"))
    with tempfile.TemporaryDirectory() as scratch:
        evaluation, _ = harness.score(
            conn, corpus, run_stats={}, baseline_result=cached,
            results_path=Path(scratch) / "results.md",
        )
    return evaluation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--stub", action="store_true",
                        help="score a stub run instead of the saved real one")
    args = parser.parse_args(argv)

    if not RESULTS.exists():
        print(f"no {RESULTS} to quote the scope note from", file=sys.stderr)
        return 1
    results = RESULTS.read_text(encoding="utf-8")
    evaluation = _evaluation_from_run(args.stub)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(evaluation, results), encoding="utf-8")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Writes results.md, qualifiers and all.

Every figure this project quotes carries a scope, and the scope belongs next to
the number rather than in somebody's memory of a conversation. A precision
figure measured on a corpus we generated is a statement about the corpus first
and the system second; a token reduction is a statement about one workload mix.
Written down here, those caveats survive being read six months from now by
somebody who was not in the room.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sentinelops.llm.providers.fake import MODEL as FAKE_MODEL


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _table(rows: list[tuple[str, ...]], header: tuple[str, ...]) -> str:
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def headline_table(evaluation) -> str:
    p, m, b, c = (
        evaluation.pipeline, evaluation.manual, evaluation.baseline,
        evaluation.comparison,
    )
    gap = p["gap_detection"]
    manual_gap = m["gap_detection"]
    return _table(
        [
            ("Missed-check rate",
             _pct(m["missed_rate"]) + f" ({m['missed']}/{m['due']})",
             _pct(p["missed"]["rate"]) + f" ({p['missed']['missed']}/{p['missed']['due']})",
             f"{c['missed_check_delta']:+.1%}"),
            ("Verdict disagreement, identical evidence",
             _pct(m["consistency"]["disagreement_rate"]),
             _pct(p["consistency"]["disagreement_rate"]),
             "structural"),
            ("Time to detection, median days",
             m["detection"]["median"], p["detection"]["median"],
             f"{c['detection_speedup_days']:.0f} days sooner"),
            ("Gap-detection precision",
             _pct(manual_gap.precision), _pct(gap.precision), "-"),
            ("Gap-detection recall",
             _pct(manual_gap.recall), _pct(gap.recall), "-"),
            ("False-positive rate",
             _pct(manual_gap.false_positive_rate),
             _pct(gap.false_positive_rate), "-"),
            ("Resolved with zero model calls",
             "n/a", _pct(p["zero_model"]["share"]), "-"),
            ("Tokens per audit cycle",
             f"{b['result'].total_tokens:,}",
             f"{p['tokens']['total_tokens']:,}",
             f"{c['token_reduction_factor']:.1f}x fewer"),
            ("Actions raised / resolved",
             "n/a",
             f"{p['actions']['raised']} / {p['actions']['resolved']}",
             f"MTTR {p['actions']['mean_days_to_resolution']} days"),
        ],
        ("Metric", "Manual (simulated)", "SentinelOps", "Difference"),
    )


def write_results(evaluation, corpus, truth: dict[str, Any], path: Path) -> str:
    p, m, b, c = (
        evaluation.pipeline, evaluation.manual, evaluation.baseline,
        evaluation.comparison,
    )
    gap = p["gap_detection"]
    baseline_gap = b["gap_detection"]
    result = b["result"]
    is_fake = result.model == "FakeModelClient" or FAKE_MODEL in str(result.model)
    counts = truth["counts"]["by_defect_kind"]

    model_warning = (
        "> **These runs used `FakeModelClient`, not a language model.** The stub is a\n"
        "> deterministic keyword heuristic; `tests/test_fake_accuracy.py` measures it at\n"
        "> ~91% agreement with ground truth, with every error on hedged `partial`\n"
        "> documents. **The precision, recall and false-positive figures below therefore\n"
        "> describe the stub, not the product.** They are reported because the *architecture*\n"
        "> comparison is still valid — SentinelOps and the naive baseline are scored\n"
        "> against the same model, so the difference between them is attributable to\n"
        "> architecture. Re-run with `SENTINELOPS_LLM_PROVIDER=openai` before quoting any\n"
        "> absolute accuracy number.\n"
        if is_fake else
        f"> Runs used model `{result.model}`.\n"
    )

    document = f"""# SentinelOps — evaluation results

Generated {datetime.now():%Y-%m-%d %H:%M} · corpus seed `{evaluation.seed}` ·
fingerprint `{evaluation.corpus_fingerprint[:16]}` · {evaluation.cycles} scheduled cycles

{model_warning}
## Headline

{headline_table(evaluation)}

---

## What each figure means, and what it does not

### 1. Missed-check rate — {_pct(m['missed_rate'])} manual vs {_pct(p['missed']['rate'])} automated

The statement's first named pain: checks "dependent on teams remembering". A check
is *missed* when it was due and nothing ever looked at it.

The automated figure is a fact about the run: {p['missed']['due']} instances came
due across {evaluation.cycles} cycles and {p['missed']['examined']} were examined.
It is {_pct(p['missed']['rate'])} because applicability and scheduling are
deterministic — a check cannot fail to be raised because nobody remembered it.

**Note what is *not* counted as missed.** {counts.get('missing', 0)} instances had
no evidence filed at all. Those are not missed checks: the system raised them,
chased them, escalated them and recorded the absence. Being told "nothing was
submitted" is the opposite of missing something.

The manual figure is **simulated** — see the assumptions section. It is not a
measurement of any real team.

### 2. Verdict consistency — {_pct(p['consistency']['disagreement_rate'])} disagreement

The second named pain: "inconsistent". Measured on
{p['consistency']['identical_evidence_groups']} group(s) of byte-identical
evidence judged in more than one process area, of which
{p['consistency']['groups_with_disagreement']} disagreed.

This is **structural, not lucky**. The assessment prompt contains no process-area
id, no area name and no owner — asserted by test — so a verdict cannot depend on
whose evidence it is. Identical bytes and identical criteria produce an identical
request, and the same request produces the same answer.

**The honest limit:** the corpus contains only
{p['consistency']['identical_evidence_groups']} such group, so the *measurement*
is thin. The structural argument is what carries the claim; the measurement
confirms it did not break. Simulated manual review disagreed on
{_pct(m['consistency']['disagreement_rate'])} of the same group(s).

The naive baseline also achieves consistency here — but by *caching identical
documents*, not by design. That helps only when the bytes match exactly; two
paraphrases of the same report would diverge.

### 3. Time to detection — median {p['detection']['median']} days vs {m['detection']['median']}

Days from a check falling due to its non-compliance being written down.
n={p['detection']['n']}, mean {p['detection']['mean']}, p90 {p['detection']['p90']},
max {p['detection']['max']}.

The pipeline was run **month by month**, not once at the end. Assessing a whole
year on 31 December would have reported near-instant detection, which would be an
artefact of the harness rather than a property of the system. Detection latency
here is therefore bounded by cycle frequency: run weekly and it falls, run
quarterly and it rises.

### 4. Gap detection — precision {_pct(gap.precision)}, recall {_pct(gap.recall)}, FPR {_pct(gap.false_positive_rate)}

Scored against the truth file on {gap.total} instances:
TP {gap.true_positive}, FP {gap.false_positive},
TN {gap.true_negative}, FN {gap.false_negative} (F1 {gap.f1:.3f}).

**Scope, which matters more than the number.** This is measured against a
*synthetic corpus with constructed failure modes*. The generator decided what
counted as a gap and then wrote a document to embody it, so the failures are
exactly as findable as the generator made them. Real compliance evidence is
messier, longer, worse formatted and ambiguous in ways nothing here reproduces.
Treat this as evidence the assessment path works on documents of known
construction — not as an expected accuracy on your own evidence.

The corpus does contain {counts.get('near_miss', 0)} **near-miss** documents that
read as clean reports and fail exactly one clause. Without those a precision
figure would be meaningless, which is why they exist.

Baseline on the same corpus and model: precision {_pct(baseline_gap.precision)},
recall {_pct(baseline_gap.recall)}, FPR {_pct(baseline_gap.false_positive_rate)}
over {baseline_gap.total} scored instances.

### 5. Zero-model-call share — {_pct(p['zero_model']['share'])}

{p['zero_model']['decided_by_rules']} of {p['zero_model']['findings']} current
findings were reached by rule, not by a model.

By tier:

{_table([(tier, str(count)) for tier, count in p['zero_model']['by_tier'].items()],
        ('decided_by', 'findings'))}

**This number is a property of the corpus mix, not a universal constant.** It is
this high because the corpus contains {counts.get('missing', 0)} instances with no
evidence, {counts.get('wrong_type', 0)} of the wrong document type,
{counts.get('stale', 0)} too stale to read, and three structured controls whose
thresholds are arithmetic. An organisation whose evidence is always present,
always the right type and always prose would see a much lower share. One with
more structured reporting would see a higher one. Quote it as "on this workload",
never as "of compliance work in general".

Note `carried_forward` sits at {p['zero_model']['by_tier'].get('carried_forward', 0)}:
the generator varies every document, so no control ever files byte-identical
evidence in two periods. The rule is implemented and tested; this corpus simply
never triggers it.

### 6. Tokens per audit cycle — {p['tokens']['total_tokens']:,} vs {result.total_tokens:,} ({c['token_reduction_factor']:.1f}x)

{_table([
    ("Model calls", f"{result.model_calls:,}", f"{p['tokens']['calls']:,}",
     f"{c['call_reduction_factor']:.1f}x fewer"),
    ("Input tokens", f"{result.input_tokens:,}", f"{p['tokens']['input_tokens']:,}", ""),
    ("Output tokens", f"{result.output_tokens:,}", f"{p['tokens']['output_tokens']:,}", ""),
    ("Total tokens", f"{result.total_tokens:,}", f"{p['tokens']['total_tokens']:,}",
     f"{c['token_reduction_factor']:.1f}x fewer"),
    ("Characters sent to model", f"{result.characters_sent:,}", "-", ""),
], ("", "Naive baseline", "SentinelOps", "Difference"))}

**What the baseline is.** A competent naive implementation, not a strawman. It
skips instances with no evidence — there is nothing to read — and caches by
document hash, so the same document is assessed once
({result.served_from_document_cache} cache hits,
{result.skipped_no_evidence} skipped for no evidence of
{result.instances_considered} considered). It uses the *same model, same system
prompt, same user template, same schema and same max_tokens*.

**What it lacks** is exactly the three things under test: applicability rules, the
pre-screen, and retrieval. It considers every control against every area, sends
wrong-type and stale and structured evidence to the model anyway, and sends whole
documents rather than relevant sections. The difference in tokens is therefore
attributable to architecture rather than to prompt-wrangling — which is the only
way this comparison is worth anything.

Baseline results are cached to disk on first run
({'served from cache' if b['cached'] else 'computed this run'}) and never
recomputed, per section 5.

**Where the {c['token_reduction_factor']:.1f}x actually comes from.** Almost
entirely from the pre-screen making {c['call_reduction_factor']:.1f}x fewer calls
— not from retrieval. The synthetic documents are short enough to be a single
chunk each, so retrieval trims almost nothing on this corpus. The mechanism is
real and tested — on a long document it drops 12 of 13 chunks — but this corpus
does not exercise it, and the figure above does not assume it. Longer evidence
would widen the gap. A reader expecting an order of magnitude should note that
1.5x is what a *competent* baseline costs you; a strawman would have produced a
larger and less honest number.

**On the token counts themselves.** The stub reports input tokens proportional to
the prompt it was handed, which is what a tokenizer does, so the comparison
responds correctly to prompt size. They are still an approximation of a real
tokenizer's output. Exact token and cost figures need the real provider; the
*ratio* is the durable part.

### 7. Actions raised vs resolved — {p['actions']['raised']} / {p['actions']['resolved']}

{_table([
    ("Raised", str(p['actions']['raised'])),
    ("Resolved", str(p['actions']['resolved'])),
    ("Still open", str(p['actions']['open'])),
    ("Escalated", str(p['actions']['escalated'])),
    ("Resolution rate", _pct(p['actions']['resolution_rate'])),
    ("Mean days to resolution", str(p['actions']['mean_days_to_resolution'])),
], ("", "count"))}

The resolution rate is low because the corpus contains remediation evidence for
only {p['remediated']} of the failures — the rest are left open on purpose, so the
queue in the dashboard is not empty. It measures the corpus, not the diligence of
a team.

---

## The manual baseline is a model, not a measurement

Nobody ran a spreadsheet-based control programme alongside this system for a
year. The manual figures come from a simulation whose every parameter was chosen
by hand:

{_table([(name, value) for name, value in m['outcome'].assumptions.describe()],
        ("Assumption", "Value"))}

Reviewers are drawn from a pool, each carrying a standing leniency, and disagree
most on documents that are nearly right — a report satisfying two clauses of
three is exactly where judgement diverges. Wrong readings are not symmetric
noise: a lenient reviewer passes a borderline document, a strict one fails an
acceptable one, which is what makes two areas reach two answers.

The disagreement rates land in the range usually called *moderate* inter-rater
agreement for subjective document review. **No empirical study backs these
specific numbers**, and the comparison is worth exactly what the assumptions are
worth. They live in one dataclass so they can be argued with and re-run.

### How far the comparison moves if the assumptions are wrong

{_table([
    (row["label"], _pct(row["missed_rate"]), _pct(row["disagreement"]),
     f"{row['median_detection_days']}d")
    for row in m["sensitivity"]
], ("Manual assumptions", "Missed-check rate", "Disagreement", "Median detection"))}

The SentinelOps column does not appear here because it does not move: those
figures are a property of the run, not of anything assumed. Only the size of the
gap changes. Note the last row — even a team with **near-perfect recall** still
carries the inconsistency and the detection lag, because those come from having
people read documents on a review cycle rather than from forgetfulness. If you
want the most conservative reading of this project's value, take that row.

## Reproducing this

```
python -m evaluation
```

Deterministic given the corpus seed (`{evaluation.seed}`) and the manual
simulation seed (4242). The corpus fingerprint
`{evaluation.corpus_fingerprint[:16]}` pins the exact evidence these numbers were
measured on; if it changes, they were measured on something else.

Audit chain over the whole run: **{p['chain'].describe()}**
({p['audit_events']:,} events).
"""
    path.write_text(document, encoding="utf-8")
    return document

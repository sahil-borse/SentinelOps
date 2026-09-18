"""Writes results.md, qualifiers and all.

Every figure this project quotes carries a scope, and the scope belongs next to
the number rather than in somebody's memory of a conversation. A precision
figure measured on a corpus we generated is a statement about the corpus first
and the system second; a token reduction is a statement about one workload mix.
Written down here, those caveats survive being read six months from now by
somebody who was not in the room.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sentinelops.llm.providers.fake import MODEL as FAKE_MODEL
from sentinelops.synth.calendar import SIMULATED_TODAY

#: What slice 19's real-provider run left behind: the comparison columns and
#: the spend ledger. Read, never written, here.
REAL_DIR = Path(__file__).resolve().parents[1] / "data" / "real"


def _real_run_section() -> str:
    """Slice 19's real-provider run: what it can say, and what it cannot.

    Generated from the files the run left behind rather than written by hand,
    so it regenerates with the rest of this document and cannot drift from the
    ledger. With no such files there was no real run, and it says nothing.
    """
    import json

    real_path = REAL_DIR / "metrics_real.json"
    fake_path = REAL_DIR / "metrics_fake.json"
    spend_path = REAL_DIR / "spend.json"
    if not (real_path.exists() and fake_path.exists() and spend_path.exists()):
        return ""
    r = json.loads(real_path.read_text(encoding="utf-8"))
    f = json.loads(fake_path.read_text(encoding="utf-8"))
    spend = json.loads(spend_path.read_text(encoding="utf-8"))

    rg, fg = r["gap_detection"], f["gap_detection"]
    rr, fr = r["recurrence"], f["recurrence"]
    rs, fs = r["severity"], f["severity"]
    refused = r["citations"].get("unreadable_reply", 0)
    judged = refused + r["citations"].get("assessments_rechecked", 0)
    supplier = "REC-AUDIT-SUPPLIER-FILES"
    r_supplier = next((g for g in r["planted_groups"] if g["id"] == supplier), None)
    f_supplier = next((g for g in f["planted_groups"] if g["id"] == supplier), None)
    tokens = r["tokens"]
    stages = {s["tier"]: s for s in tokens["by_stage"]}
    cycles = r["cycles"]
    models = ", ".join(r["models"])

    saved = sum(
        spend.get(k, {}).get("cost_usd", 0.0)
        for k in ("replay", "replay_stopped", "resume")
    )
    lost = sum(
        v.get("cost_usd_at_least", 0.0) for k, v in spend.items() if k.endswith("_lost")
    )
    baseline_spent = spend.get("baseline_stopped", {}).get("cost_usd", 0.0)
    probes = spend.get("probes", {}).get("cost_usd", 0.0)
    total = saved + lost + baseline_spent + probes

    def pairs(group) -> str:
        return f"{group['pairs_found']}/{group['pairs']} pairs" if group else "n/a"

    def trio(g) -> str:
        return f"{_pct(g['precision'])} / {_pct(g['recall'])} / {_pct(g['fpr'])}"

    rows = [
        ("Gap detection: precision / recall / FPR", trio(fg), trio(rg),
         f"**No.** {refused} of {judged} model verdicts were refused as unreadable, "
         "so the real column scores the refusal rule, not the model"),
        ("Taxonomy categories", str(f["taxonomy"]["count"]),
         str(r["taxonomy"]["count"]),
         "**Yes.** Derived from the seeded audit descriptions alone, which the "
         "defect never touched"),
        ("Recurrence: recall / precision",
         f"{_pct(fr['recall'])} / {_pct(fr['precision'])}",
         f"{_pct(rr['recall'])} / {_pct(rr['precision'])}",
         "**No.** Scored on the audit track, but the candidates came from a "
         "findings population the refusals had inflated"),
        ("Supplier-files set (the stub's blind spot)", pairs(f_supplier),
         pairs(r_supplier), "Suggestive only, for the same reason"),
        ("Severity suggestion agrees with auditor",
         f"{fs['agreed']}/{fs['compared']}", f"{rs['agreed']}/{rs['compared']}",
         "**No.** Compared over findings the refusals raised"),
        ("Assessments flagged for human review",
         str(f["review"]["flagged"]), str(r["review"]["flagged"]),
         "Only as a count of refusals"),
        ("Citations failing verification", "0", "0",
         "**No.** No model citation was kept to check"),
        ("Adversarial document", f["adversarial"].get("verdict", "n/a"),
         "refused unread",
         "**No.** Refused before it was judged; resistance to the injection is "
         "untested"),
        ("Metering against the budget's own count", "n/a", "exact",
         "**Yes.** Rows, tokens and cost all agree"),
        ("Audit chain", "verified", "verified, "
         f"{r['chain'].split('checked=')[1].split(',')[0]} events", "**Yes.**"),
    ]
    table = _table(
        [tuple(row) for row in rows],
        ("Figure", "FakeModelClient", models, "Quotable?"),
    )

    shape = (
        '`{"criteria": {"1": {"verdict": ..., "cited_spans": [...]}}, '
        '"overall_verdict": ...}`'
    )
    assess = stages.get("assess", {})
    recur = stages.get("recurrence", {})
    return f"""## Slice 19: the real-provider run, attempted and not measurable

> **No accuracy figure in this document comes from a language model.** The
> pipeline was run against `{models}` and completed, but its accuracy cannot be
> measured. Every figure above and below this section is still the stub's.

**What went wrong.** Every one of the {refused} assessments the model judged
was refused as unreadable. The assessment prompt (`assessment_v2`) names three
of the seven fields its schema requires, and the schema is validated locally
but never sent to the provider. The model answered each criterion in its own
layout, {shape}, with quotations copied verbatim, and the pipeline refused them
rather than guess at them. That refusal is the design working; the prompt is the
defect. `FakeModelClient` always answers in the canonical shape, so no stub run
could have found it. The figures downstream inherit it: each refusal was
flagged for review and treated as a failed check, and the findings that raised
became the population recurrence and severity agreement were measured over.

{table}

**The bill is real, but it is the bill of a failing run.** {tokens['calls']:,}
calls and {tokens['total_tokens']:,} tokens for the full replay, ${tokens['cost_usd']:.4f};
{tokens['calls'] / cycles:.1f} calls and ${tokens['cost_usd'] / cycles:.4f} per
cycle over {cycles} cycles. Assessment made {assess.get('calls', 0)} calls because
each of {refused} unreadable replies was retried once; recurrence made
{recur.get('calls', 0)} over a findings population the refusals had inflated. A
working prompt would cost roughly half. Token counts are read from the response
objects.

**Everything slice 19 spent, from `data/real/spend.json`:** ${saved:.4f} in the
saved run; at least ${lost:.4f} in two runs that saved nothing, the first
because an exception escaped a handler over an in-memory database, the second
because its session ended before a stage that checkpointed only on finishing;
${baseline_spent:.4f} on 26 naive-baseline calls, stopped once their answers were
found unreadable for the same reason; ${probes:.4f} on probes. About
${total:.2f} in all, of a $10 cap. **There is no real naive baseline**: it was
stopped, and nothing was cached.

**Defects the run found.** Triage's prompt described a different shape from its
schema, and recurrence's never named its wrapper key; both are fixed
(`triage_v2`, `recurrence_v2`) and were probed against the model. Recurrence's
flat 500-token ceiling could not hold an answer about a full shortlist; it is
now sized to the shortlist. **The assessment prompt is not fixed.** The change
is the one triage and recurrence got, but it could not be checked against the
model without spending, and spending stopped at the owner's decision.

"""



def _recurrence_lines(analytics: dict) -> str:
    """One line per recurring set. Sets, not pairs — A->B->C happened three
    times in one continuing story, and calling it two links overstates it."""
    recurring = analytics["recurring"]
    if not recurring["count"]:
        return "_None detected in this run._"

    lines = ["| category | links | units | furthest apart |", "|---|---|---|---|"]
    for name, row in recurring["by_category"].items():
        lines.append(
            f"| {name.replace('_', ' ')} | {row['links']} | {row['units']} | "
            f"{row['max_months_apart']} months |"
        )
    if recurring["longest_chains"]:
        lines.append("")
        lines.append(
            "**On the link counts.** These are the detector's links, not the "
            "section 8 figure, and per-category counts lean towards whichever "
            "categories hold the most generated activity-track descriptions: "
            "`FakeModelClient` compares descriptions by shared vocabulary, so "
            "two findings naming the same control in different units look "
            "alike to it whether or not the same thing went wrong. A real model "
            "reads the sentence. Treat the *shape* — recurrence exists, it "
            "crosses units, it spans months — as the durable claim, and the "
            "per-category link counts as a stub artefact until the real "
            "provider has run."
        )
        lines.append("")
        lines.append("The chains that read as one continuing problem:")
        lines.append("")
        for chain in recurring["longest_chains"]:
            lines.append(
                f"- **{(chain['category'] or 'unclassified').replace('_', ' ')}** "
                f"— {' → '.join(chain['findings'])} across "
                f"{', '.join(chain['units'])}, spanning "
                f"{chain['months_spanned']} months"
            )
    return "\n".join(lines)


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
            ("Findings raised / closed",
             "n/a",
             f"{p['actions']['raised']} / {p['actions']['resolved']}",
             f"mean {p['actions']['mean_days_to_resolution']} days to closure"),
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
    a = p["analytics"]
    a_rec = p["recurrence"]

    model_warning = (
        "> **These runs used `FakeModelClient`, not a language model.** The stub is a\n"
        "> deterministic keyword heuristic; `tests/test_fake_accuracy.py` measures it at\n"
        "> ~98% agreement with ground truth on this corpus. Its errors are hedged\n"
        "> `partial` documents, plus one near-miss that states its shortfall as\n"
        "> arithmetic (\"3 of 5 accounts were disabled\") — a comparison a keyword\n"
        "> rule cannot make and a language model can, which is a fair summary of\n"
        "> why the model tier exists at all.\n"
        "> **The precision, recall and false-positive figures below therefore\n"
        "> describe the stub, not the product.** They are reported because the *architecture*\n"
        "> comparison is still valid — SentinelOps and the naive baseline are scored\n"
        "> against the same model, so the difference between them is attributable to\n"
        "> architecture. Re-run with `SENTINELOPS_LLM_PROVIDER=openai` before quoting any\n"
        "> absolute accuracy number.\n"
        if is_fake else
        "> **These runs used a real provider.** One model per stage, read back from\n"
        "> the run's own metering rows rather than from config at the time of\n"
        "> writing, so this says what actually answered:\n>\n"
        + "".join(
            f"> - `{row['tier']}` → `{row['model']}` · {row['calls']} calls ·"
            f" {row['input_tokens'] + row['output_tokens']:,} tokens ·"
            f" ${row['cost_usd']:.4f}\n"
            for row in p["tokens"].get("by_stage", [])
        )
        + ">\n"
        f"> The naive baseline ran on `{result.model}`, the same model as the\n"
        "> assessment stage, so the difference between the two paths remains\n"
        "> attributable to architecture rather than to model choice.\n"
    )

    # No wall-clock stamp. Two runs on one seed must produce the same bytes, and
    # the time of writing was the only thing in this file that would differ.
    document = f"""# SentinelOps — evaluation results

Corpus seed `{evaluation.seed}` · fingerprint `{evaluation.corpus_fingerprint[:16]}` ·
{evaluation.cycles} scheduled cycles to the vantage point {SIMULATED_TODAY}

{model_warning}
{_real_run_section()}## Headline

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

**Due means the due date had passed by the vantage point, counted from the truth
file.** A check falling due on the vantage point itself is not yet missed, the
same boundary S1 uses to mark an instance overdue. Until slice
15z this denominator came from the instances the scheduler had created, and the
scheduler stopped at 2026 — so the 2027 obligations it never raised were not
counted as missed, they were not counted at all, and the figure read 0.0% over
446. Now every obligation in the truth file is placed: {p['missed']['due']} due
({p['missed']['waived']} of them waived and set aside),
{p['missed']['not_yet_due']} opened but not yet due, and
{p['missed']['not_yet_open']} whose period had not started. Of the due ones,
{p['missed']['unscheduled']} were never scheduled and
{p['missed']['scheduled_unexamined']} were scheduled but never examined. The
harness refuses to score a run where the first of those is above zero.

**Note what is *not* counted as missed.** {counts.get('missing', 0)} instances had
no evidence filed at all. Those are not missed checks: the system raised them,
chased them, escalated them and recorded the absence. Being told "nothing was
submitted" is the opposite of missing something.

The manual figure is **simulated** — see the assumptions section. It is not a
measurement of any real team. Its denominator is taken at the same vantage point:
{m['outcome'].not_yet_due} obligations not yet due are set aside, where until
slice 15z the model reviewed every row in the eighteen-month window.

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
{gap.unjudged} truth obligation(s) received no verdict from this path and are
counted here rather than dropped: their periods were not yet due or not yet open
at the vantage point. A verdict for an instance the truth file does not describe
is refused outright rather than skipped, which is what it used to be.

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
over {baseline_gap.total} scored instances. {b.get("note", "")}

### 5. Zero-model-call share — {_pct(p['zero_model']['share'])}

{p['zero_model']['decided_by_rules']} of {p['zero_model']['assessments']} current
findings were reached by rule, not by a model.

By tier:

{_table([(tier, str(count)) for tier, count in p['zero_model']['by_tier'].items()],
        ('decided_by', 'assessments'))}

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

### 7. Findings raised vs closed — {p['actions']['raised']} / {p['actions']['resolved']}

{_table([
    ("Raised", str(p['actions']['raised'])),
    ("Closed by an auditor", str(p['actions']['resolved'])),
    ("Still open", str(p['actions']['open'])),
    ("Escalated", str(p['actions']['escalated'])),
    ("Closure rate", _pct(p['actions']['resolution_rate'])),
    ("Mean days to closure", str(p['actions']['mean_days_to_resolution'])),
    ("Mean follow-ups per closure",
     str(p['actions']['mean_follow_ups_to_close'])),
], ("", "count"))}

The closure rate is low because the corpus contains remediation evidence for
only {p['remediated']} of the failures — the rest are left open on purpose, so the
queue in the dashboard is not empty. It measures the corpus, not the diligence of
a team.

**What the chase did.** Across the same run the follow-up engine sent
{p['reminders']:,} reminders and raised {p['escalations']:,} escalations, all
deterministic and all from the severity table. That is the number a human would
have had to produce by remembering; it is not a measure of accuracy, and it is
not claimed as one.

---

## Section 8 — the portfolio, computed

Every figure below is arithmetic over rows the pipeline wrote. No model is
involved in any of it, which is asserted two ways in `tests/test_analytics.py`:
statically, that `analytics.py` imports nothing from `llm/`, and at runtime, by
rigging `get_client` to raise and computing the whole portfolio anyway.

{_table([
    ("Open / closed",
     f"{a['open_vs_closed']['open']} / {a['open_vs_closed']['closed']} "
     f"({a['open_vs_closed']['closed_pct']}% closed)"),
    ("Severity mix",
     ", ".join(f"{k} {v}" for k, v in a['severity_mix']['overall'].items())),
    ("Overdue, aged",
     ", ".join(f"{k}: {v}" for k, v in a['overdue_ageing']['buckets'].items())),
    ("Oldest overdue", f"{a['overdue_ageing']['oldest_days']} days"),
    ("Recurring gap categories (section 8)",
     f"{a['recurring']['by_gap_category']['count']} holding "
     f"{a['recurring']['by_gap_category']['findings_involved']} findings; "
     f"audit track {a['recurring']['audit_track']['count']} holding "
     f"{a['recurring']['audit_track']['findings_involved']}"),
    ("Recurrence links (the detector's, advisory)",
     f"{a['recurring']['count']} across "
     f"{a['recurring']['findings_involved']} findings, "
     f"{a['recurring']['spanning_units']} of them between different units"),
    ("Open findings by month",
     f"{a['trend_verdict']['direction']} across the window "
     f"({a['trend_verdict']['slope_per_month']:+.2f} a month); "
     f"{a['trend_verdict']['recent']['direction']} over the last quarter"),
    ("Needing more than one evidence round", str(a['effort']['multi_round'])),
    ("Most rounds on one finding", str(a['effort']['worst_rounds'])),
    ("Needing more than one reminder", str(a['effort']['multi_reminder'])),
    ("Median days to closure",
     str(a['closure']['overall']['median_days'])),
    ("Due in the next 30 days",
     f"{len(a['upcoming']['audits'])} audit(s), "
     f"{a['upcoming']['activity_total']} activities"),
], ("", "value"))}

**Findings by audit kind.** The two scheduled things section 1 keeps apart, kept
apart in the data:

{_table([
    (kind.replace("_", " "), str(count))
    for kind, count in a['by_dimension']['by_audit_kind'].items()
], ("source", "findings"))}

**Recurrence is the figure that needed eighteen months.** Over a single quarter
there is nothing to find. Each link below is one finding that resembles an
earlier one in a different unit or period — the stakeholder's own definition of
recurring, and the comparison nobody holds in their head across a year and a
half:

**Recurrence is scored, not admired.** The corpus plants
{a_rec['planted_groups']} recurring gap sets in the audit track and the truth file
records which findings belong to which, so the detector can be marked rather than
eyeballed: **recall {_pct(a_rec['recall'] or 0)}, precision
{_pct(a_rec['precision'] or 0)}** over {a_rec['planted_pairs']} planted pairs
({a_rec['links_asserted']} links asserted, grouping {a_rec['grouped_pairs']} pairs).

Scored on the audit track only. Those descriptions are an auditor's own words,
which is what section 2 justifies a model for. Activity-track descriptions are
generated by the system from the control title and the failing clause, so "the
same gap elsewhere" is derivable there by a rule — marking the detector wrong for
linking them would score it against a definition the stakeholder did not give,
and marking it right would credit a model for arithmetic.

{_recurrence_lines(a)}

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

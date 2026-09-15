# SentinelOps — evaluation results

Generated 2026-09-15 21:08 · corpus seed `20260831` ·
fingerprint `d180c3f6c453433d` · 16 scheduled cycles

> **These runs used `FakeModelClient`, not a language model.** The stub is a
> deterministic keyword heuristic; `tests/test_fake_accuracy.py` measures it at
> ~98% agreement with ground truth on this corpus. Its errors are hedged
> `partial` documents, plus one near-miss that states its shortfall as
> arithmetic ("3 of 5 accounts were disabled") — a comparison a keyword
> rule cannot make and a language model can, which is a fair summary of
> why the model tier exists at all.
> **The precision, recall and false-positive figures below therefore
> describe the stub, not the product.** They are reported because the *architecture*
> comparison is still valid — SentinelOps and the naive baseline are scored
> against the same model, so the difference between them is attributable to
> architecture. Re-run with `SENTINELOPS_LLM_PROVIDER=openai` before quoting any
> absolute accuracy number.

## Headline

| Metric | Manual (simulated) | SentinelOps | Difference |
|---|---|---|---|
| Missed-check rate | 18.8% (91/483) | 0.0% (0/482) | +18.8% |
| Verdict disagreement, identical evidence | 100.0% | 0.0% | structural |
| Time to detection, median days | 102 | 0.0 | 102 days sooner |
| Gap-detection precision | 66.7% | 95.2% | - |
| Gap-detection recall | 63.8% | 93.8% | - |
| False-positive rate | 4.3% | 0.6% | - |
| Resolved with zero model calls | n/a | 29.6% | - |
| Tokens per audit cycle | 462,098 | 313,545 | 1.5x fewer |
| Findings raised / closed | n/a | 113 / 93 | mean 32.5 days to closure |

---

## What each figure means, and what it does not

### 1. Missed-check rate — 18.8% manual vs 0.0% automated

The statement's first named pain: checks "dependent on teams remembering". A check
is *missed* when it was due and nothing ever looked at it.

The automated figure is a fact about the run: 482 instances came
due across 16 cycles and 482 were examined.
It is 0.0% because applicability and scheduling are
deterministic — a check cannot fail to be raised because nobody remembered it.

**Due means the due date had passed by the vantage point, counted from the truth
file.** A check falling due on the vantage point itself is not yet missed, the
same boundary S1 uses to mark an instance overdue. Until slice
15z this denominator came from the instances the scheduler had created, and the
scheduler stopped at 2026 — so the 2027 obligations it never raised were not
counted as missed, they were not counted at all, and the figure read 0.0% over
446. Now every obligation in the truth file is placed: 482 due
(1 of them waived and set aside),
170 opened but not yet due, and
36 whose period had not started. Of the due ones,
0 were never scheduled and
0 were scheduled but never examined. The
harness refuses to score a run where the first of those is above zero.

**Note what is *not* counted as missed.** 5 instances had
no evidence filed at all. Those are not missed checks: the system raised them,
chased them, escalated them and recorded the absence. Being told "nothing was
submitted" is the opposite of missing something.

The manual figure is **simulated** — see the assumptions section. It is not a
measurement of any real team. Its denominator is taken at the same vantage point:
206 obligations not yet due are set aside, where until
slice 15z the model reviewed every row in the eighteen-month window.

### 2. Verdict consistency — 0.0% disagreement

The second named pain: "inconsistent". Measured on
1 group(s) of byte-identical
evidence judged in more than one process area, of which
0 disagreed.

This is **structural, not lucky**. The assessment prompt contains no process-area
id, no area name and no owner — asserted by test — so a verdict cannot depend on
whose evidence it is. Identical bytes and identical criteria produce an identical
request, and the same request produces the same answer.

**The honest limit:** the corpus contains only
1 such group, so the *measurement*
is thin. The structural argument is what carries the claim; the measurement
confirms it did not break. Simulated manual review disagreed on
100.0% of the same group(s).

The naive baseline also achieves consistency here — but by *caching identical
documents*, not by design. That helps only when the bytes match exactly; two
paraphrases of the same report would diverge.

### 3. Time to detection — median 0.0 days vs 102

Days from a check falling due to its non-compliance being written down.
n=16, mean 4.9, p90 13,
max 13.

The pipeline was run **month by month**, not once at the end. Assessing a whole
year on 31 December would have reported near-instant detection, which would be an
artefact of the harness rather than a property of the system. Detection latency
here is therefore bounded by cycle frequency: run weekly and it falls, run
quarterly and it rises.

### 4. Gap detection — precision 95.2%, recall 93.8%, FPR 0.6%

Scored against the truth file on 550 instances:
TP 60, FP 3,
TN 483, FN 4 (F1 0.945).
139 truth obligation(s) received no verdict from this path and are
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

The corpus does contain 39 **near-miss** documents that
read as clean reports and fail exactly one clause. Without those a precision
figure would be meaningless, which is why they exist.

Baseline on the same corpus and model: precision 92.5%,
recall 61.3%, FPR 0.7%
over 684 scored instances.

### 5. Zero-model-call share — 29.6%

163 of 550 current
findings were reached by rule, not by a model.

By tier:

| decided_by | assessments |
|---|---|
| no_evidence | 4 |
| s3_model | 387 |
| stale_evidence | 1 |
| structured_threshold | 157 |
| wrong_evidence_type | 1 |

**This number is a property of the corpus mix, not a universal constant.** It is
this high because the corpus contains 5 instances with no
evidence, 14 of the wrong document type,
14 too stale to read, and three structured controls whose
thresholds are arithmetic. An organisation whose evidence is always present,
always the right type and always prose would see a much lower share. One with
more structured reporting would see a higher one. Quote it as "on this workload",
never as "of compliance work in general".

Note `carried_forward` sits at 0:
the generator varies every document, so no control ever files byte-identical
evidence in two periods. The rule is implemented and tested; this corpus simply
never triggers it.

### 6. Tokens per audit cycle — 313,545 vs 462,098 (1.5x)

|  | Naive baseline | SentinelOps | Difference |
|---|---|---|---|
| Model calls | 683 | 453 | 1.5x fewer |
| Input tokens | 419,903 | 284,297 |  |
| Output tokens | 42,195 | 29,248 |  |
| Total tokens | 462,098 | 313,545 | 1.5x fewer |
| Characters sent to model | 604,387 | - |  |

**What the baseline is.** A competent naive implementation, not a strawman. It
skips instances with no evidence — there is nothing to read — and caches by
document hash, so the same document is assessed once
(1 cache hits,
316 skipped for no evidence of
1000 considered). It uses the *same model, same system
prompt, same user template, same schema and same max_tokens*.

**What it lacks** is exactly the three things under test: applicability rules, the
pre-screen, and retrieval. It considers every control against every area, sends
wrong-type and stale and structured evidence to the model anyway, and sends whole
documents rather than relevant sections. The difference in tokens is therefore
attributable to architecture rather than to prompt-wrangling — which is the only
way this comparison is worth anything.

Baseline results are cached to disk on first run
(served from cache) and never
recomputed, per section 5.

**Where the 1.5x actually comes from.** Almost
entirely from the pre-screen making 1.5x fewer calls
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

### 7. Findings raised vs closed — 113 / 93

|  | count |
|---|---|
| Raised | 113 |
| Closed by an auditor | 93 |
| Still open | 20 |
| Escalated | 62 |
| Closure rate | 82.3% |
| Mean days to closure | 32.5 |
| Mean follow-ups per closure | 1.1 |

The closure rate is low because the corpus contains remediation evidence for
only 102 of the failures — the rest are left open on purpose, so the
queue in the dashboard is not empty. It measures the corpus, not the diligence of
a team.

**What the chase did.** Across the same run the follow-up engine sent
134 reminders and raised 124 escalations, all
deterministic and all from the severity table. That is the number a human would
have had to produce by remembering; it is not a measure of accuracy, and it is
not claimed as one.

---

## Section 8 — the portfolio, computed

Every figure below is arithmetic over rows the pipeline wrote. No model is
involved in any of it, which is asserted two ways in `tests/test_analytics.py`:
statically, that `analytics.py` imports nothing from `llm/`, and at runtime, by
rigging `get_client` to raise and computing the whole portfolio anyway.

|  | value |
|---|---|
| Open / closed | 20 / 93 (82.3% closed) |
| Severity mix | Major 40, Minor 48, Observation 25 |
| Overdue, aged | 0-30: 2, 31-60: 2, 61-90: 0, 90+: 6 |
| Oldest overdue | 377 days |
| Recurring gap categories (section 8) | 9 holding 113 findings; audit track 6 holding 24 |
| Recurrence links (the detector's, advisory) | 162 across 87 findings, 135 of them between different units |
| Open findings by month | rising across the window (+1.02 a month); flat over the last quarter |
| Needing more than one evidence round | 18 |
| Most rounds on one finding | 3 |
| Needing more than one reminder | 23 |
| Median days to closure | 31 |
| Due in the next 30 days | 1 audit(s), 19 activities |

**Findings by audit kind.** The two scheduled things section 1 keeps apart, kept
apart in the data:

| source | findings |
|---|---|
| compliance activity | 86 |
| internal audit | 11 |
| qarev | 7 |
| release audit | 5 |
| document review | 4 |

**Recurrence is the figure that needed eighteen months.** Over a single quarter
there is nothing to find. Each link below is one finding that resembles an
earlier one in a different unit or period — the stakeholder's own definition of
recurring, and the comparison nobody holds in their head across a year and a
half:

**Recurrence is scored, not admired.** The corpus plants
2 recurring gap sets in the audit track and the truth file
records which findings belong to which, so the detector can be marked rather than
eyeballed: **recall 50.0%, precision
75.0%** over 6 planted pairs
(3 links asserted, grouping 4 pairs).

Scored on the audit track only. Those descriptions are an auditor's own words,
which is what section 2 justifies a model for. Activity-track descriptions are
generated by the system from the control title and the failing clause, so "the
same gap elsewhere" is derivable there by a rule — marking the detector wrong for
linking them would score it against a definition the stakeholder did not give,
and marking it right would credit a model for arithmetic.

| category | links | units | furthest apart |
|---|---|---|---|
| change not authorised | 54 | 8 | 13 months |
| access not revoked | 29 | 7 | 9 months |
| documentation out of date | 23 | 7 | 11 months |
| incident follow up incomplete | 17 | 4 | 13 months |
| periodic review overdue | 17 | 8 | 11 months |
| backup or continuity untested | 12 | 4 | 13 months |
| training not completed | 8 | 5 | 8 months |
| data retention or privacy | 2 | 2 | 6 months |

**On the link counts.** These are the detector's links, not the section 8 figure, and per-category counts lean towards whichever categories hold the most generated activity-track descriptions: `FakeModelClient` compares descriptions by shared vocabulary, so two findings naming the same control in different units look alike to it whether or not the same thing went wrong. A real model reads the sentence. Treat the *shape* — recurrence exists, it crosses units, it spans months — as the durable claim, and the per-category link counts as a stub artefact until the real provider has run.

The chains that read as one continuing problem:

- **training not completed** — FND-IA-2026-H1-03 → FND-TRAINING-IT-2026-Q2 → FND-TRAINING-PRJ-ATLAS-2026-Q3 → FND-TRAINING-PRJ-CORAL-2027-Q1 across HR, IT, Project Atlas, Project Coral, spanning 13 months
- **access not revoked** — FND-ACCESS-REVIEW-IT-2026-Q1 → FND-ACCESS-REVIEW-PRJ-ATLAS-2026-Q4 → FND-ACCESS-REVIEW-PRJ-CORAL-2027-Q1 across IT, Project Atlas, Project Coral, spanning 11 months
- **access not revoked** — FND-FINDING-CLOSURE-HR-2026-Q2 → FND-FINDING-CLOSURE-HR-2026-Q3 → FND-EXTERNAL-AUDIT-READY-HR-2026 across HR, spanning 6 months
- **access not revoked** — FND-IA-2026-H1-01 → FND-IA-2026-H2-01 → FND-QA-2027-Q1-01 across Admin, HR, IT, spanning 11 months
- **training not completed** — FND-IA-2026-H1-03 → FND-TRAINING-IT-2026-Q2 → FND-TRAINING-PRJ-DELTA-2026-Q3 across HR, IT, Project Delta, spanning 7 months

---

## The manual baseline is a model, not a measurement

Nobody ran a spreadsheet-based control programme alongside this system for a
year. The manual figures come from a simulation whose every parameter was chosen
by hand:

| Assumption | Value |
|---|---|
| recall, monthly control | 88% |
| recall, quarterly control | 76% |
| recall, annual control | 62% |
| reviewer pool | 6 |
| leniency spread | ±0.45 |
| inconsistency factor | 0.55 |
| review cycle | 90 days |
| write-up lag | 12 days |
| missed checks surface after | 240 days |

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

| Manual assumptions | Missed-check rate | Disagreement | Median detection |
|---|---|---|---|
| as reported | 18.8% | 100.0% | 102d |
| diligent team (recall +10pp, half the inconsistency) | 9.3% | 0.0% | 72d |
| stretched team (recall -10pp, more drift) | 28.6% | 0.0% | 132d |
| near-perfect recall, inconsistency unchanged | 0.4% | 100.0% | 102d |

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

Deterministic given the corpus seed (`20260831`) and the manual
simulation seed (4242). The corpus fingerprint
`d180c3f6c453433d` pins the exact evidence these numbers were
measured on; if it changes, they were measured on something else.

Audit chain over the whole run: **OK - 6132 entries, chain intact**
(6,132 events).

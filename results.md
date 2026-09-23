# SentinelOps — evaluation results

Corpus seed `20260831` · fingerprint `d180c3f6c453433d` ·
16 scheduled cycles to the vantage point 2027-04-15

> **These runs used a real provider.** One model per stage, read back from
> the run's own metering rows rather than from config at the time of
> writing, so this says what actually answered:
>
> - `assess` → `gpt-4.1-mini-2025-04-14` · 453 calls · 406,171 tokens · $0.2541
> - `recurrence` → `gpt-4.1-mini-2025-04-14` · 160 calls · 187,389 tokens · $0.0895
> - `triage` → `gpt-4.1-mini-2025-04-14` · 36 calls · 66,545 tokens · $0.0500
>
> The naive baseline ran on `gpt-4.1-mini`, the same model as the
> assessment stage, so the difference between the two paths remains
> attributable to architecture rather than to model choice.

## The real-provider run

The pipeline was replayed to the vantage point against `gpt-4.1-mini-2025-04-14`:
649 calls, 660,105 tokens, $0.3935.
Read back from the run's own metering rows, so this says what actually answered:

> - `assess` → `gpt-4.1-mini-2025-04-14` · 453 calls · 406,171 tokens · $0.2541
> - `recurrence` → `gpt-4.1-mini-2025-04-14` · 160 calls · 187,389 tokens · $0.0895
> - `triage` → `gpt-4.1-mini-2025-04-14` · 36 calls · 66,545 tokens · $0.0500

**Assessment against assessment, which is the comparison that holds.** The pipeline judged the same evidence in 453 calls and 406,171 tokens; the naive baseline needed 683 calls and 607,678. That is 1.5x the calls and 1.5x the tokens for the same job. The totals below and in the headline include classification and recurrence, which the naive path does not do at all — so the total ratio compares a pipeline doing more work against a baseline doing less, and on a real model it runs the other way.

**What the accuracy figures are measured on has not changed.** They describe a
*synthetic corpus with constructed failure modes* — the generator decided what
counted as a gap and then wrote a document to embody it. Section 4's scope note
applies to the real column exactly as it applies to the stub's.

| Figure | FakeModelClient | gpt-4.1-mini-2025-04-14 | Quotable? |
|---|---|---|---|
| Gap detection: precision / recall / FPR | 95.2% / 93.8% / 0.6% | 94.1% / 100.0% / 0.8% | **Yes**, on this corpus — see the scope note under section 4 |
| Confusion (TP/FP/TN/FN) | 60/3/483/4 | 64/4/482/0 | **Yes**, on this corpus — see the scope note under section 4 |
| Taxonomy categories derived | 9 | 7 | **Yes.** Read off the auditors' own descriptions, which no stage rewrites |
| Recurrence: recall / precision | 50.0% / 75.0% | 66.7% / 28.6% | **Yes**, over 6 planted pairs on the audit track — a thin measurement, and thin either way |
| The supplier-files set, which the stub misses entirely | 0/3 pairs | 1/3 pairs | **Yes.** Named because it is the case a keyword rule cannot reach: three findings sharing no vocabulary |
| Assessments flagged for human review | 1 of 652 | 35 of 652 | **Yes.** A count of what the pipeline would not assert alone |
| Citations failing verification, and discarded | 0 | 0 | **Yes.** Every kept citation re-checked against the evidence it was taken from, character for character |
| Verdicts refused: reply unreadable / citation not in the evidence | 0 / 0 | 0 / 0 | **Yes.** The refusal rules, counted separately because they are different failures |
| Severity suggestion agrees with the auditor | 38/86 (44.2%) | 77/146 (52.7%) | **Yes**, as a measure of the suggestion's usefulness — never a score the system should maximise, since the auditor assigns |
| The adversarial document | gap | gap | **Yes.** One planted injection, so it is a demonstration rather than a rate |
| Injection obeyed | no | no | **Yes**, for that one document |
| Model calls, full replay | 575 | 649 | **Yes.** Counted, not estimated |
| Tokens, full replay | 435,719 | 660,105 | Real column **yes** — read from each response object. Stub column **no**: its counts are proportional to the prompt, not a tokenizer's |
| Cost, full replay | $0.1771 | $0.3935 | Real column **yes**, at the published rates in `llm/models.py`. Stub column **no** — the shape of a bill, not a bill |
| Per cycle | 35.9 calls, $0.0111 | 40.6 calls, $0.0246 | **Yes**, over 16 cycles of this corpus |
| Audit chain | verified | verified | **Yes.** Recomputed over every entry |

**Everything spent, from `data/real/spend.json`:** $1.98 across every
attempt, of a $10 cap. That includes the runs that produced nothing: an early
replay whose handler let an exception past it over an in-memory database, a
resume killed with its session before the stage it was in had saved, and a
naive baseline stopped once its answers were found unreadable. Those are on the
ledger because they were paid for.

**What the failures were.** Nearly all of them were one defect: a prompt that did
not state the shape its schema required, with the schema validated locally and
never sent to the provider. **All eight prompts had it**, and the last two —
taxonomy's propose and consolidate — were found only after a replay had paid for
453 assessments, because an unstated shape is one a model guesses right much of
the time. `FakeModelClient` always answers in the canonical shape, so no stub run
could have found any of them.

Two token ceilings were below what their own schemas permit, and truncation is
fatal rather than short. A closed-set field answered with a value outside the set
ended a run where it should have asked again: `gpt-4.1-mini` wrote
`reliable_or_inadequate_record_keeping` for a taxonomy holding
`unreliable_or_inadequate_record_keeping`. It is now asked once more with the
permitted values restated, the batch is halved to find which finding is at issue,
and one that still cannot be named is left uncategorised and reported rather than
mislabelled or fatal. Two stages also built a client before checking whether they
had any work, so scoring a finished run demanded a provider in order to do
nothing. All are fixed, each with a test that fails without a provider.

## Headline

| Metric | Manual (simulated) | SentinelOps | Difference |
|---|---|---|---|
| Missed-check rate | 18.8% (91/483) | 0.0% (0/482) | +18.8% |
| Verdict disagreement, identical evidence | 100.0% | 0.0% | structural |
| Time to detection, median days | 102 | 13.0 | 89 days sooner |
| Gap-detection precision | 66.7% | 94.1% | - |
| Gap-detection recall | 63.8% | 100.0% | - |
| False-positive rate | 4.3% | 0.8% | - |
| Resolved with zero model calls | n/a | 29.6% | - |
| Tokens per audit cycle | 607,678 | 660,105 | 0.9x fewer |
| Findings raised / closed | n/a | 173 / 89 | mean 32.0 days to closure |

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

### 3. Time to detection — median 13.0 days vs 102

Days from a check falling due to its non-compliance being written down.
n=80, mean 15.5, p90 43,
max 105.

The pipeline was run **month by month**, not once at the end. Assessing a whole
year on 31 December would have reported near-instant detection, which would be an
artefact of the harness rather than a property of the system. Detection latency
here is therefore bounded by cycle frequency: run weekly and it falls, run
quarterly and it rises.

### 4. Gap detection — precision 94.1%, recall 100.0%, FPR 0.8%

Scored against the truth file on 550 instances:
TP 64, FP 4,
TN 482, FN 0 (F1 0.970).
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

Baseline on the same corpus and model: precision 35.9%,
recall 86.2%, FPR 20.4%
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

### 6. Tokens per audit cycle — 660,105 vs 607,678 (0.9x)

|  | Naive baseline | SentinelOps | Difference |
|---|---|---|---|
| Model calls | 683 | 649 | 1.1x fewer |
| Input tokens | 493,724 | 551,544 |  |
| Output tokens | 113,954 | 108,561 |  |
| Total tokens | 607,678 | 660,105 | 0.9x fewer |
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

Baseline results are cached to disk on first run and never recomputed, per
section 5. Whether *this* run read that cache or filled it is deliberately not
recorded here: it is a fact about the disk, not about the corpus or the seed,
and reporting it made two runs on one seed produce different bytes — which the
determinism test exists to forbid.

**Where the 0.9x actually comes from.** Almost
entirely from the pre-screen making 1.1x fewer calls
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

### 7. Findings raised vs closed — 173 / 89

|  | count |
|---|---|
| Raised | 173 |
| Closed by an auditor | 89 |
| Still open | 84 |
| Escalated | 113 |
| Closure rate | 51.4% |
| Mean days to closure | 32.0 |
| Mean follow-ups per closure | 1.1 |

The closure rate is low because the corpus contains remediation evidence for
only 0 of the failures — the rest are left open on purpose, so the
queue in the dashboard is not empty. It measures the corpus, not the diligence of
a team.

**What the chase did.** Across the same run the follow-up engine sent
0 reminders and raised 0 escalations, all
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
| Open / closed | 84 / 89 (51.4% closed) |
| Severity mix | Major 38, Minor 100, Observation 35 |
| Overdue, aged | 0-30: 5, 31-60: 8, 61-90: 5, 90+: 52 |
| Oldest overdue | 408 days |
| Recurring gap categories (section 8) | 6 holding 172 findings; audit track 5 holding 25 |
| Recurrence links (the detector's, advisory) | 189 across 121 findings, 103 of them between different units |
| Open findings by month | rising across the window (+5.47 a month); rising over the last quarter |
| Needing more than one evidence round | 18 |
| Most rounds on one finding | 3 |
| Needing more than one reminder | 80 |
| Median days to closure | 31 |
| Due in the next 30 days | 1 audit(s), 19 activities |

**Findings by audit kind.** The two scheduled things section 1 keeps apart, kept
apart in the data:

| source | findings |
|---|---|
| compliance activity | 146 |
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
eyeballed: **recall 66.7%, precision
28.6%** over 6 planted pairs
(10 links asserted, grouping 14 pairs).

Scored on the audit track only. Those descriptions are an auditor's own words,
which is what section 2 justifies a model for. Activity-track descriptions are
generated by the system from the control title and the failing clause, so "the
same gap elsewhere" is derivable there by a rule — marking the detector wrong for
linking them would score it against a definition the stakeholder did not give,
and marking it right would credit a model for arithmetic.

| category | links | units | furthest apart |
|---|---|---|---|
| lack of required validation or approval | 70 | 9 | 13 months |
| unreliable or inadequate record keeping | 68 | 4 | 11 months |
| outdated or uncontrolled documentation | 36 | 9 | 9 months |
| unauthorized or excess access | 11 | 4 | 11 months |
| incomplete due diligence | 3 | 3 | 5 months |
| falsified or unverified test results | 1 | 2 | 8 months |

**On the link counts.** These are the detector's links, not the section 8 figure, and per-category counts lean towards whichever categories hold the most generated activity-track descriptions: `FakeModelClient` compares descriptions by shared vocabulary, so two findings naming the same control in different units look alike to it whether or not the same thing went wrong. A real model reads the sentence. Treat the *shape* — recurrence exists, it crosses units, it spans months — as the durable claim, and the per-category link counts as a stub artefact until the real provider has run.

The chains that read as one continuing problem:

- **unreliable or inadequate record keeping** — FND-INCIDENT-PM-IT-2026-02 → FND-INCIDENT-PM-FINANCE-2026-04 → FND-INCIDENT-PM-FINANCE-2026-05 → FND-INCIDENT-PM-FINANCE-2026-07 → FND-INCIDENT-PM-FINANCE-2026-08 across Finance, IT, spanning 6 months
- **unreliable or inadequate record keeping** — FND-INCIDENT-PM-IT-2026-02 → FND-INCIDENT-PM-FINANCE-2026-04 → FND-INCIDENT-PM-FINANCE-2026-05 → FND-INCIDENT-PM-FINANCE-2026-07 → FND-INCIDENT-PM-FINANCE-2026-09 across Finance, IT, spanning 7 months
- **unreliable or inadequate record keeping** — FND-INCIDENT-PM-IT-2026-02 → FND-INCIDENT-PM-FINANCE-2026-04 → FND-INCIDENT-PM-FINANCE-2026-05 → FND-INCIDENT-PM-FINANCE-2026-07 → FND-INCIDENT-PM-FINANCE-2026-11 across Finance, IT, spanning 9 months
- **unreliable or inadequate record keeping** — FND-INCIDENT-PM-IT-2026-02 → FND-INCIDENT-PM-FINANCE-2026-04 → FND-INCIDENT-PM-FINANCE-2026-05 → FND-INCIDENT-PM-FINANCE-2026-06 across Finance, IT, spanning 4 months
- **unreliable or inadequate record keeping** — FND-INCIDENT-PM-IT-2026-02 → FND-INCIDENT-PM-IT-2026-03 → FND-INCIDENT-PM-IT-2026-07 → FND-INCIDENT-PM-IT-2026-08 across IT, spanning 6 months

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

Audit chain over the whole run: **OK - 7771 entries, chain intact**
(7,771 events).

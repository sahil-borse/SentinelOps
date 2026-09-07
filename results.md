# SentinelOps — evaluation results

Generated 2026-09-08 01:36 · corpus seed `20260831` ·
fingerprint `836a9a93fc6ba563` · 21 scheduled cycles

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
| Missed-check rate | 18.8% (153/813) | 0.0% (0/531) | +18.8% |
| Verdict disagreement, identical evidence | 100.0% | 0.0% | structural |
| Time to detection, median days | 102.0 | 13 | 89 days sooner |
| Gap-detection precision | 67.5% | 98.1% | - |
| Gap-detection recall | 77.6% | 98.1% | - |
| False-positive rate | 4.2% | 0.2% | - |
| Resolved with zero model calls | n/a | 29.3% | - |
| Tokens per audit cycle | 366,637 | 314,122 | 1.2x fewer |
| Findings raised / closed | n/a | 94 / 73 | mean 29.5 days to closure |

---

## What each figure means, and what it does not

### 1. Missed-check rate — 18.8% manual vs 0.0% automated

The statement's first named pain: checks "dependent on teams remembering". A check
is *missed* when it was due and nothing ever looked at it.

The automated figure is a fact about the run: 531 instances came
due across 21 cycles and 531 were examined.
It is 0.0% because applicability and scheduling are
deterministic — a check cannot fail to be raised because nobody remembered it.

**Note what is *not* counted as missed.** 10 instances had
no evidence filed at all. Those are not missed checks: the system raised them,
chased them, escalated them and recorded the absence. Being told "nothing was
submitted" is the opposite of missing something.

The manual figure is **simulated** — see the assumptions section. It is not a
measurement of any real team.

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

### 3. Time to detection — median 13 days vs 102.0

Days from a check falling due to its non-compliance being written down.
n=17, mean -23.5, p90 43,
max 44.

The pipeline was run **month by month**, not once at the end. Assessing a whole
year on 31 December would have reported near-instant detection, which would be an
artefact of the harness rather than a property of the system. Detection latency
here is therefore bounded by cycle frequency: run weekly and it falls, run
quarterly and it rises.

### 4. Gap detection — precision 98.1%, recall 98.1%, FPR 0.2%

Scored against the truth file on 532 instances:
TP 53, FP 1,
TN 477, FN 1 (F1 0.981).

**Scope, which matters more than the number.** This is measured against a
*synthetic corpus with constructed failure modes*. The generator decided what
counted as a gap and then wrote a document to embody it, so the failures are
exactly as findable as the generator made them. Real compliance evidence is
messier, longer, worse formatted and ambiguous in ways nothing here reproduces.
Treat this as evidence the assessment path works on documents of known
construction — not as an expected accuracy on your own evidence.

The corpus does contain 38 **near-miss** documents that
read as clean reports and fail exactly one clause. Without those a precision
figure would be meaningless, which is why they exist.

Baseline on the same corpus and model: precision 97.1%,
recall 63.0%, FPR 0.2%
over 527 scored instances.

### 5. Zero-model-call share — 29.3%

156 of 532 current
findings were reached by rule, not by a model.

By tier:

| decided_by | assessments |
|---|---|
| no_evidence | 5 |
| s3_model | 376 |
| stale_evidence | 11 |
| structured_threshold | 140 |

**This number is a property of the corpus mix, not a universal constant.** It is
this high because the corpus contains 10 instances with no
evidence, 14 of the wrong document type,
16 too stale to read, and three structured controls whose
thresholds are arithmetic. An organisation whose evidence is always present,
always the right type and always prose would see a much lower share. One with
more structured reporting would see a higher one. Quote it as "on this workload",
never as "of compliance work in general".

Note `carried_forward` sits at 0:
the generator varies every document, so no control ever files byte-identical
evidence in two periods. The rule is implemented and tested; this corpus simply
never triggers it.

### 6. Tokens per audit cycle — 314,122 vs 366,637 (1.2x)

|  | Naive baseline | SentinelOps | Difference |
|---|---|---|---|
| Model calls | 526 | 438 | 1.2x fewer |
| Input tokens | 333,648 | 285,525 |  |
| Output tokens | 32,989 | 28,597 |  |
| Total tokens | 366,637 | 314,122 | 1.2x fewer |
| Characters sent to model | 506,509 | - |  |

**What the baseline is.** A competent naive implementation, not a strawman. It
skips instances with no evidence — there is nothing to read — and caches by
document hash, so the same document is assessed once
(1 cache hits,
309 skipped for no evidence of
836 considered). It uses the *same model, same system
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

**Where the 1.2x actually comes from.** Almost
entirely from the pre-screen making 1.2x fewer calls
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

### 7. Findings raised vs closed — 94 / 73

|  | count |
|---|---|
| Raised | 94 |
| Closed by an auditor | 73 |
| Still open | 21 |
| Escalated | 57 |
| Closure rate | 77.7% |
| Mean days to closure | 29.5 |
| Mean follow-ups per closure | 1.1 |

The closure rate is low because the corpus contains remediation evidence for
only 100 of the failures — the rest are left open on purpose, so the
queue in the dashboard is not empty. It measures the corpus, not the diligence of
a team.

**What the chase did.** Across the same run the follow-up engine sent
354 reminders and raised 114 escalations, all
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
| Open / closed | 21 / 73 (77.7% closed) |
| Severity mix | Major 31, Minor 40, Observation 23 |
| Overdue, aged | 0-30: 0, 31-60: 0, 61-90: 0, 90+: 21 |
| Oldest overdue | 596 days |
| Recurrence links | 132 across 79 findings, 104 of them between different units |
| Needing more than one evidence round | 16 |
| Most rounds on one finding | 3 |
| Needing more than one reminder | 31 |
| Median days to closure | 31 |
| Due in the next 30 days | 1 audit(s), 0 activities |

**Findings by audit kind.** The two scheduled things section 1 keeps apart, kept
apart in the data:

| source | findings |
|---|---|
| compliance activity | 77 |
| internal audit | 6 |
| qarev | 4 |
| release audit | 4 |
| document review | 3 |

**Recurrence is the figure that needed eighteen months.** Over a single quarter
there is nothing to find. Each link below is one finding that resembles an
earlier one in a different unit or period — the stakeholder's own definition of
recurring, and the comparison nobody holds in their head across a year and a
half:

| category | links | units | furthest apart |
|---|---|---|---|
| control not performed | 91 | 10 | 13 months |
| access not recertified | 12 | 6 | 9 months |
| training not completed | 12 | 6 | 6 months |
| third party due diligence | 10 | 5 | 9 months |
| data retention or privacy | 5 | 3 | 12 months |
| access not revoked | 2 | 2 | 7 months |

**On the link counts.** `control_not_performed` is over-represented, and the reason is the stub rather than the corpus: `FakeModelClient` compares descriptions by shared vocabulary, so two findings naming the same control in different units look alike to it whether or not the same thing went wrong. A real model reads the sentence. Treat the *shape* — recurrence exists, it crosses units, it spans months — as the durable claim, and the per-category counts as a stub artefact until the real provider has run.

The chains that read as one continuing problem:

- **access not revoked** — FND-IA-2026-H1-01 → FND-IA-2026-H2-01 → FND-QA-2027-Q1-01 across IT Services, Payments Processing, spanning 11 months
- **control not performed** — FND-INCIDENT-PM-ITSVC-2026-01 → FND-INCIDENT-PM-PLATFORM-2026-01 → FND-REL-2027-04-02 across IT Services, Platform Engineering, spanning 14 months
- **control not performed** — FND-INCIDENT-PM-ITSVC-2026-01 → FND-INCIDENT-PM-PLATFORM-2026-01 → FND-INCIDENT-PM-PLATFORM-2026-02 across IT Services, Platform Engineering, spanning 1 months
- **control not performed** — FND-INCIDENT-PM-ITSVC-2026-01 → FND-INCIDENT-PM-PLATFORM-2026-01 → FND-INCIDENT-PM-PLATFORM-2026-05 across IT Services, Platform Engineering, spanning 5 months
- **control not performed** — FND-INCIDENT-PM-ITSVC-2026-01 → FND-INCIDENT-PM-FINREP-2026-02 → FND-CRYPTO-KEY-PAYMENTS-2026-Q2 across Financial Reporting, IT Services, Payments Processing, spanning 6 months

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
| diligent team (recall +10pp, half the inconsistency) | 7.9% | 0.0% | 72d |
| stretched team (recall -10pp, more drift) | 26.9% | 100.0% | 132d |
| near-perfect recall, inconsistency unchanged | 0.7% | 0.0% | 102d |

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
`836a9a93fc6ba563` pins the exact evidence these numbers were
measured on; if it changes, they were measured on something else.

Audit chain over the whole run: **OK - 5296 entries, chain intact**
(5,296 events).

# SentinelOps — evaluation results

Generated 2026-09-02 01:45 · corpus seed `20260831` ·
fingerprint `7e7ee16b4e1eebd9` · 15 scheduled cycles

> **These runs used `FakeModelClient`, not a language model.** The stub is a
> deterministic keyword heuristic; `tests/test_fake_accuracy.py` measures it at
> ~91% agreement with ground truth, with every error on hedged `partial`
> documents. **The precision, recall and false-positive figures below therefore
> describe the stub, not the product.** They are reported because the *architecture*
> comparison is still valid — SentinelOps and the naive baseline are scored
> against the same model, so the difference between them is attributable to
> architecture. Re-run with `SENTINELOPS_LLM_PROVIDER=openai` before quoting any
> absolute accuracy number.

## Headline

| Metric | Manual (simulated) | SentinelOps | Difference |
|---|---|---|---|
| Missed-check rate | 17.2% (59/343) | 0.0% (0/342) | +17.2% |
| Verdict disagreement, identical evidence | 100.0% | 0.0% | structural |
| Time to detection, median days | 102 | 13.0 | 89 days sooner |
| Gap-detection precision | 82.1% | 95.5% | - |
| Gap-detection recall | 71.4% | 93.4% | - |
| False-positive rate | 5.8% | 1.6% | - |
| Resolved with zero model calls | n/a | 41.1% | - |
| Tokens per audit cycle | 216,146 | 147,791 | 1.5x fewer |
| Actions raised / resolved | n/a | 154 / 7 | MTTR 24.1 days |

---

## What each figure means, and what it does not

### 1. Missed-check rate — 17.2% manual vs 0.0% automated

The statement's first named pain: checks "dependent on teams remembering". A check
is *missed* when it was due and nothing ever looked at it.

The automated figure is a fact about the run: 342 instances came
due across 15 cycles and 342 were examined.
It is 0.0% because applicability and scheduling are
deterministic — a check cannot fail to be raised because nobody remembered it.

**Note what is *not* counted as missed.** 33 instances had
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

### 3. Time to detection — median 13.0 days vs 102

Days from a check falling due to its non-compliance being written down.
n=148, mean 3.6, p90 16,
max 16.

The pipeline was run **month by month**, not once at the end. Assessing a whole
year on 31 December would have reported near-instant detection, which would be an
artefact of the harness rather than a property of the system. Detection latency
here is therefore bounded by cycle frequency: run weekly and it falls, run
quarterly and it rises.

### 4. Gap detection — precision 95.5%, recall 93.4%, FPR 1.6%

Scored against the truth file on 343 instances:
TP 85, FP 4,
TN 248, FN 6 (F1 0.944).

**Scope, which matters more than the number.** This is measured against a
*synthetic corpus with constructed failure modes*. The generator decided what
counted as a gap and then wrote a document to embody it, so the failures are
exactly as findable as the generator made them. Real compliance evidence is
messier, longer, worse formatted and ambiguous in ways nothing here reproduces.
Treat this as evidence the assessment path works on documents of known
construction — not as an expected accuracy on your own evidence.

The corpus does contain 47 **near-miss** documents that
read as clean reports and fail exactly one clause. Without those a precision
figure would be meaningless, which is why they exist.

Baseline on the same corpus and model: precision 93.1%,
recall 59.3%, FPR 1.8%
over 310 scored instances.

### 5. Zero-model-call share — 41.1%

141 of 343 current
findings were reached by rule, not by a model.

By tier:

| decided_by | findings |
|---|---|
| no_evidence | 33 |
| s3_model | 202 |
| stale_evidence | 16 |
| structured_threshold | 77 |
| wrong_evidence_type | 15 |

**This number is a property of the corpus mix, not a universal constant.** It is
this high because the corpus contains 33 instances with no
evidence, 15 of the wrong document type,
16 too stale to read, and three structured controls whose
thresholds are arithmetic. An organisation whose evidence is always present,
always the right type and always prose would see a much lower share. One with
more structured reporting would see a higher one. Quote it as "on this workload",
never as "of compliance work in general".

Note `carried_forward` sits at 0:
the generator varies every document, so no control ever files byte-identical
evidence in two periods. The rule is implemented and tested; this corpus simply
never triggers it.

### 6. Tokens per audit cycle — 147,791 vs 216,146 (1.5x)

|  | Naive baseline | SentinelOps | Difference |
|---|---|---|---|
| Model calls | 309 | 205 | 1.5x fewer |
| Input tokens | 195,786 | 133,445 |  |
| Output tokens | 20,360 | 14,346 |  |
| Total tokens | 216,146 | 147,791 | 1.5x fewer |
| Characters sent to model | 296,652 | - |  |

**What the baseline is.** A competent naive implementation, not a strawman. It
skips instances with no evidence — there is nothing to read — and caches by
document hash, so the same document is assessed once
(1 cache hits,
222 skipped for no evidence of
532 considered). It uses the *same model, same system
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

### 7. Actions raised vs resolved — 154 / 7

|  | count |
|---|---|
| Raised | 154 |
| Resolved | 7 |
| Still open | 147 |
| Escalated | 140 |
| Resolution rate | 4.5% |
| Mean days to resolution | 24.1 |

The resolution rate is low because the corpus contains remediation evidence for
only 6 of the failures — the rest are left open on purpose, so the
queue in the dashboard is not empty. It measures the corpus, not the diligence of
a team.

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
| as reported | 17.2% | 100.0% | 102d |
| diligent team (recall +10pp, half the inconsistency) | 7.0% | 0.0% | 72d |
| stretched team (recall -10pp, more drift) | 28.3% | 0.0% | 132d |
| near-perfect recall, inconsistency unchanged | 0.3% | 100.0% | 102d |

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
`7e7ee16b4e1eebd9` pins the exact evidence these numbers were
measured on; if it changes, they were measured on something else.

Audit chain over the whole run: **OK - 2466 entries, chain intact**
(2,466 events).

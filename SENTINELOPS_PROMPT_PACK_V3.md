# SentinelOps — Prompt Pack v3

Team Transformers · Embi AI Nexus 2026 · solo · video due **9 Sep 2026**

Ten prompts, one per session, in order. Repo: `D:\projects\SentinelOps`,
spec saved as `CLAUDE.md`, Python 3.11.9 in `.venv`.

---

## Session ritual

**Open every session with this, then the slice prompt:**

> Re-read CLAUDE.md and PROGRESS.md before doing anything. State in one sentence
> which slice we are on and what already exists, then implement only that slice.

**Close every session with:**

> List every file you created or changed with one line each on what it does. Run
> the tests. Append one line to PROGRESS.md describing this slice.

Read that list. If you can't say what a file does, ask before moving on.
Then commit in GitHub Desktop: `slice N: <what it does>`.

**Stuck rule:** 90 minutes on one problem → stub it, note it in `STUBS.md`,
commit, move on.

---

## Schedule

| Date | Slice |
|---|---|
| Thu 27 Aug | 1 — foundations + llm boundary |
| Fri 28 Aug | 2 — synthetic data |
| Sat 29 Aug | 3 — applicability |
| Sun 30 Aug | 4 — trigger, routing, audit |
| Mon 31 Aug | 5 — pre-screen |
| Tue 1 Sep | 6 — assessment ⚠ needs API key |
| Wed 2 Sep | 7 — flagging + closed loop |
| **Thu 3 Sep** | **AI JAM Session 1** |
| Fri 4 Sep | 8 — evaluation harness ⚠ needs key |
| Sat 5 Sep | 8b audit pack + 9 dashboard — **CODE FREEZE** |
| Sun 6 Sep | Script + record |
| **Mon 7 Sep** | **AI JAM Session 2** |
| Tue 8 Sep | Edit |
| Wed 9 Sep | Submit, morning |

Slices 1–5 need no API key.

---

## Slice 1 — Foundations and llm boundary · 27 Aug

> Read CLAUDE.md fully before doing anything. Then state in one sentence what this
> project is and which slice we're on, and implement slice 1 only. Do not build
> ahead into later slices.
>
> **Project setup.** Python 3.11. `pyproject.toml`, `src/sentinelops/`, pytest.
> SQLite behind a thin repository layer using plain `sqlite3` — no ORM.
>
> **Domain entities.** Implement all eight entities from section 3 as dataclasses
> with tables and repositories: ProcessArea, ControlDefinition, CheckInstance,
> Evidence, Finding, Action, ComplianceException, AuditEvent.
>
> AuditEvent is append-only — its repository exposes append and read methods only,
> no update, no delete. Write a test asserting those methods don't exist.
>
> **The llm/ service boundary.** Create `src/sentinelops/llm/` as an isolated
> provider boundary:
> `protocol.py` — LlmRequest (system, messages, max_tokens, response_schema),
> LlmResponse (text, parsed_json, input_tokens, output_tokens, cached_tokens,
> model, latency_ms), and an LlmClient protocol with a single
> `complete(request) -> LlmResponse` method.
> `providers/fake.py` — FakeModelClient returning deterministic canned JSON with
> plausible token counts.
> `providers/openai.py` — real client, stubbed with NotImplementedError for now.
> `factory.py` — returns a client based on the SENTINELOPS_LLM_PROVIDER env var,
> defaulting to fake.
> `metering.py` — TokenMeter, a context manager wrapping every call, recording
> tier, model, input_tokens, output_tokens, cached_tokens, latency_ms and computed
> cost to a `token_usage` table.
> `prompts/` — prompt templates as versioned functions, not inline f-strings.
> System prompt constant and placed first; no variable interpolation into the prefix.
>
> Retries, JSON parsing and repair, schema validation, error mapping and token
> extraction all live inside `llm/`. No provider SDK type may cross the boundary —
> add a test walking every module outside `llm/` asserting none import a provider SDK.
>
> Token counts come from the response object. Never estimated, never computed from
> character counts.
>
> **One end-to-end path.** In `main.py`: one process area, one control definition,
> one evidence document, one assessment via the fake client, one finding written,
> one action raised, one audit event appended, one token usage row recorded.
> Hardcoded is fine — this is a skeleton, not a feature.
>
> **Constraints.** No web framework. No CLI beyond `main.py`. No config system.
> No abstract base class hierarchies — protocols and plain functions. Under 500
> lines excluding tests.
>
> **When done.** Run the tests. Then show me the finding record, the action, the
> audit events, the token usage row, and a list of every file you created with one
> line on what each does.

---

## Slice 2 — Synthetic data · 28 Aug

> Slice 2 only. Build the seeded, reproducible synthetic data generator from
> section 7 of CLAUDE.md. Same seed, same corpus, every run.
>
> Generate 6–8 process areas with genuinely varied attributes (handles_pii,
> customer_facing, has_suppliers, region, criticality) and named owners.
>
> Generate 12–15 controls across monthly, quarterly and annual frequencies with
> realistic criteria text: access reviews, vendor due diligence, data retention,
> incident post-mortems, training completion, backup verification, supplier
> security attestation. **At least three must have evidence_kind = structured**
> (training completion tables, backup logs, access review exports) — the statement
> says "process data or documents" and both must be demonstrable.
>
> Generate a 12-month calendar so recurrence, overdue and escalation actually occur.
>
> Generate evidence of mixed quality: compliant, partial, non-compliant, stale,
> wrong-type, missing. Include **near-miss documents** that read as compliant but
> fail exactly one clause. Include **the same evidence submitted for the same
> control in two different process areas**, so verdict consistency is measurable.
> Include 2–3 ComplianceExceptions, one expiring mid-year. Include remediation
> evidence for several injected gaps.
>
> Write a truth file recording every injected gap — instance, failing clause,
> expected verdict — to a path the pipeline never reads. Add a test asserting no
> module under `src/sentinelops/` imports it.
>
> Show me: one compliant document, one near-miss, one structured evidence record,
> the exception list, and the matching truth file rows.

---

## Slice 3 — S0 Applicability · 29 Aug

> Slice 3 only. Build S0, the applicability rules engine.
>
> Each ControlDefinition carries an `applies_when` expression over process-area
> attributes. Evaluate deterministically to produce the applicable control set per
> area. Keep the expression format simple and readable — you will explain it on camera.
>
> Tests: two areas with different attributes get different control sets; an area
> matching no controls is handled cleanly; the tier makes zero model calls — assert
> this by injecting a client that raises if called.
>
> Show me the applicable control sets for two contrasting areas, side by side,
> with the count difference.

---

## Slice 4 — S1 Trigger, routing, audit · 30 Aug

> Slice 4 only. Build S1, the scheduling and trigger engine.
>
> Generate CheckInstances from control frequency across the simulated calendar.
> State machine: pending, submitted, assessed, overdue, waived. Compute due,
> due-soon and overdue from the simulated current date. Escalate overdue instances
> up an owner chain after a configured interval. Route each instance to its owning
> team by logging a notification payload — never send anything.
>
> Active ComplianceExceptions suppress instance generation for that control and
> area. An exception past its expiry date raises its own alert.
>
> Every state change appends an AuditEvent with ts, actor (system|ai|user), owner,
> action, entity_type, entity_id and detail. Enforce append-only at the repository
> layer and test it.
>
> Expose a single `run_cycle(as_of_date)` entry point that performs the whole
> cycle, plus `advance_calendar(days)`. The scheduler must contain no logic beyond
> calling run_cycle — the same path is used by cron, a UI button and the CLI.
> Record in the audit trail whether a run was system- or human-triggered.
> Running a cycle twice for the same period must not duplicate instances.
>
> Zero model calls — assert it.
>
> Show me the audit timeline for one check instance across three months including
> an overdue escalation, and the alert raised by the expired exception.

---

## Slice 5 — S2 Pre-screen · 31 Aug

> Slice 5 only. Build S2, the pre-screen tier. Its job is to resolve everything
> resolvable before any model call.
>
> In order: no evidence → insufficient_evidence; wrong document type →
> insufficient_evidence; content hash unchanged since the last assessed period →
> carry the prior finding forward flagged carried_forward; older than the control's
> freshness_days → gap by rule; evidence_kind == structured with a numeric
> threshold → evaluate directly in code and produce a full Finding with a rationale
> naming the numbers.
>
> Only ambiguous document evidence survives to S3.
>
> Instrument it: record how many instances exit at each rule and what share of the
> corpus never reaches a model.
>
> Show me the exit-rate breakdown per rule over the full corpus, and one structured
> evaluation finding.

---

## Slice 6 — S3 Assessment · 1 Sep · **API key needed**

> Slice 6 only. Build S3 and implement `providers/openai.py` for real.
>
> Chunk document evidence and retrieve only the sections relevant to the control
> criteria. Never send a whole document.
>
> One model call per surviving instance. Strict JSON: verdict (enum: compliant |
> partial | gap | insufficient_evidence), confidence, rationale, cited_spans, gaps,
> recommended_action, needs_human_review.
>
> cited_spans must contain exact quoted text or character offsets from the evidence.
> A verdict without citations is a bug — add a test that rejects one.
>
> Confidence below threshold sets needs_human_review rather than asserting a
> verdict. Hard max_tokens. Malformed JSON retried once, then failed cleanly with
> the instance marked for human review.
>
> System prompt constant and placed first — no variable interpolation into the
> prefix. This is what makes identical evidence produce identical verdicts across
> areas; add a test asserting the same evidence in two areas yields the same verdict.
>
> Read the API key from a `.env` file via environment variable. Never hardcode it.
> FakeModelClient must keep working — tests still run without a key.
>
> Show me one near-miss assessment with its citations, the consistency test result,
> and the token usage row.

---

## Slice 7 — S4 Flagging, actions, the closed loop · 2 Sep

> Slice 7 only. Build S4 — flagging, routing and the resolution loop. This is the
> slice the statement most explicitly asks for and it must work end to end.
>
> Classify every non-compliant outcome into exactly one of the statement's three
> categories: **gap** (content fails criteria), **exception** (approved deviation,
> or an expired one), **overdue** (no evidence by due date — raised with no model
> call). Keep them distinct in the data and in the UI later.
>
> Severity from a documented formula: control severity_weight × verdict ×
> area criticality × overdue duration. Deterministic, reproducible, explainable
> in one sentence.
>
> Every non-compliant finding raises an **Action** assigned to the owning team with
> a due date, moving through raised → assigned → in_progress →
> remediation_submitted → reassessed → resolved | escalated.
>
> When remediation evidence is submitted, the instance re-enters S2/S3. A new
> Finding is written with supersedes_finding_id set. If it passes, the Action
> resolves with a resolution_note. Actions overdue past their own due date escalate
> on their own timer, separately from the check.
>
> Add a `reassess(check_instance_id)` entry point so remediation can be re-checked
> on demand rather than waiting for the next cycle.
>
> Every transition appends an AuditEvent with the owner recorded.
>
> Show me one complete lifecycle: gap found → action raised → remediation submitted
> → re-assessed → resolved, with the full audit timeline printed.

---

## Slice 8 — Evaluation harness · 4 Sep · **API key needed**

> Slice 8 only. Build the evaluation harness and produce `results.md`.
>
> Implement the naive baseline: every check instance, full evidence plus full
> criteria straight to the large model, no rules, no pre-screen, no reuse. Same
> model, same task — a fair comparison with no architecture.
> **Cache baseline results to disk on first run and never re-run them.**
>
> Run both pipelines over the identical corpus and report all seven metrics from
> section 6: missed-check rate simulated-manual vs automated; verdict variance for
> the same control across areas; time-to-detection of non-compliance; precision,
> recall and false-positive rate on gap detection vs the truth file; share of
> instances resolved with zero model calls; tokens per audit cycle both paths with
> the reduction factor; actions raised vs resolved and mean time to resolution.
>
> For the manual baseline, simulate reviewer inconsistency — the same evidence
> judged differently — so the consistency comparison is meaningful.
>
> Write `results.md` and print the table.

---

## Slice 8b — Audit Evidence Pack · 5 Sep · the differentiator

> Slice 8b only. Build the Audit Evidence Pack generator.
>
> Given a date range and scope, produce a single auditor-ready document containing:
> cover (organisation, period, generation timestamp, scope); coverage summary
> (every area, every applicable control, instances due / completed / waived /
> missed); exception register (rationale, approver, grant and expiry dates, whether
> lapsed); findings register (verdict, confidence, **cited evidence excerpt
> inline**, whether human-reviewed); action register (what was found, who owned it,
> when raised, what was submitted, when re-assessed, how closed); full
> chronological trail (timestamp, actor, owner); and a one-page method note.
>
> **Critical constraint: generate the pack from the audit log alone. Never from
> current-state tables.** Add a test asserting the generator imports no live-state
> repository. This constraint is the entire point — it proves the trail is complete.
>
> Add point-in-time reconstruction: the same generator with an `as_of` date
> replays the log to that date and renders posture as it stood.
>
> Output as HTML or markdown that renders cleanly on screen for the video.
>
> Show me a generated pack for the full year, and one reconstructed as of a
> mid-year date.

---

## Slice 9 — Dashboard · 5 Sep · **CODE FREEZE at the end**

> Slice 9 only. Build the UI — Streamlit, or FastAPI with a single HTML page.
> Whichever is fastest. This is not a frontend exercise.
>
> One screen: compliance status by process area; overdue and escalation queue;
> finding detail with **cited spans highlighted inside the source document**; open
> actions with owners, due dates and status; audit timeline for a selected check
> instance; live token and cost meter; calendar-advance control; a "run cycle now"
> button; a "re-assess" button on a check; and a button to generate the audit pack.
>
> The highlighted-citation view is the shot the video is built around. Make that
> one look good and keep everything else plain and legible.
>
> Fully operable without touching a terminal.
>
> Then freeze. No features after this.

---

## Slice 10 — Video · 6–8 Sep

Not code. Script word for word against section 10 of the spec and the shot list in
`SENTINELOPS_DEMO_DESIGN.md`. Record audio separately from screen capture. Edit to
about 7 minutes.

One prompt worth running first:

> Read CLAUDE.md and results.md. Write a 7-minute video script following section
> 10. Plain spoken English, short sentences, no marketing language. Mark which
> screen should be visible for each paragraph.

Then rewrite it in your own voice.

---

## If you fall behind

Cut from the top: point-in-time reconstruction (keep the pack) · calendar-advance
UI control · audit timeline visualisation (keep the data) · the second structured
control · mean-time-to-resolution.

**Never cut:** citations, the truth file, the closed action loop, the near-miss
flag, the baseline comparison, the audit pack, the dashboard, the video.

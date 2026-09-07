# SentinelOps — Prompt Pack

Team Transformers · Embi AI Nexus 2026 · solo · video due **9 Sep 2026**
Slices 1 and 2 are done. Start at slice 3.

Repo `D:\projects\SentinelOps` · Python 3.11.9 in `.venv` · spec at `CLAUDE.md` ·
history and reasoning at `CONTEXT.md`.

---

## Session ritual

**Open with:**

> Re-read CLAUDE.md and PROGRESS.md before doing anything. State in one sentence
> which slice we are on and what already exists, then implement only that slice.

**Close with:**

> List every file you created or changed with one line each on what it does. Run
> the tests. Append one line to PROGRESS.md describing this slice.

Read that list. If you can't say what a file does, ask before moving on.
Then commit: `slice N: <what it does>`.

**90-minute rule:** stuck longer on one problem → stub it, note it in `STUBS.md`,
commit, move on.

---

## Schedule

| Date | Slice |
|---|---|
| Sat 29 Aug | 3 — applicability |
| Sun 30 Aug | 4 — trigger, routing, audit |
| Mon 31 Aug | 5 — pre-screen |
| Tue 1 Sep | 6 — assessment ⚠ needs API key |
| Wed 2 Sep | 7 — flagging + closed loop |
| **Thu 3 Sep** | **AI JAM Session 1** |
| Fri 4 Sep | 8 — evaluation harness ⚠ needs key |
| Sat 5 Sep | 8b audit pack · 9 dashboard · **CODE FREEZE** |
| Sun 6 Sep | Script + record |
| **Mon 7 Sep** | **AI JAM Session 2** |
| Tue 8 Sep | Edit |
| Wed 9 Sep | Submit, morning |

Slices 3–5 need no API key. Get the key before Monday night.

---

## Slice 3 — S0 Applicability · 29 Aug

> Slice 3 only. Build S0, the applicability rules engine.
>
> Each ControlDefinition carries an `applies_when` expression over process-area
> attributes. Evaluate deterministically to produce the applicable control set per
> area. Keep the expression format simple and readable — it has to be explained on
> camera in one sentence.
>
> The generator's trivial `applies()` stand-in from slice 2 established 64
> area×control pairings, pinned by `test_applicability_matches_every_generated_pair`.
> The real engine must reproduce all 64. Do not weaken that test to make it pass.
>
> Tests: two areas with different attributes get different control sets; an area
> matching no controls is handled cleanly; the stage makes zero model calls —
> assert this by injecting a client that raises if called.
>
> Show me the applicable control sets for two contrasting areas side by side, with
> the count difference.

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
> area. An exception past its expiry raises its own alert. EXC-002 lapses
> 2026-06-30 — Q1 and Q2 suppressed, Q3 and Q4 return.
>
> Every state change appends an AuditEvent with ts, actor (system|ai|user), owner,
> action, entity_type, entity_id, detail. Append-only enforced at the repository
> layer, with a test.
>
> Expose a single `run_cycle(as_of_date)` entry point performing the whole cycle,
> plus `advance_calendar(days)`. The scheduler contains no logic beyond calling
> run_cycle — cron, a UI button and the CLI all use the same path. Record in the
> audit trail whether a run was system- or human-triggered. Running a cycle twice
> for the same period must not duplicate instances; key on control × area × period.
>
> Zero model calls — assert it.
>
> Show me the audit timeline for one check instance across three months including
> an overdue escalation, and the alert raised by the lapsed exception.

---

## Slice 5 — S2 Pre-screen · 31 Aug

> Slice 5 only. Build S2, the pre-screen tier. Its job is to resolve everything
> resolvable before any model call.
>
> In order: no evidence → insufficient_evidence; wrong document type →
> insufficient_evidence; content hash unchanged since the last assessed period →
> carry the prior finding forward flagged carried_forward; older than the control's
> freshness_days → gap by rule; evidence_kind == structured with a numeric
> threshold → evaluate directly in code and produce a full Finding whose rationale
> names the numbers.
>
> Only ambiguous document evidence survives to S3.
>
> Evidence is write-once. Re-submission creates a new Evidence record, never an
> update. Add a test.
>
> Instrument it: record how many instances exit at each rule and what share of the
> corpus never reaches a model.
>
> Show me the exit-rate breakdown per rule over the full corpus, and one structured
> evaluation finding.

---

## Slice 6 — S3 Assessment · 1 Sep · **API key needed**

Two security items fold in here because the assessment path is open. Retrofitting
them later costs several times more.

> Slice 6 only. Build S3 and implement `providers/openai.py` for real.
>
> Chunk document evidence and retrieve only the sections relevant to the control
> criteria. Never send a whole document.
>
> One model call per surviving instance. Strict JSON: verdict (enum: compliant |
> partial | gap | insufficient_evidence), confidence, rationale, cited_spans, gaps,
> recommended_action, needs_human_review.
>
> **Citations must resolve.** cited_spans contain exact quoted text from the
> evidence. Verify every span actually appears in the source document; if any does
> not, the assessment fails rather than returning a verdict. Add a test.
>
> **Prompt injection defence.** Evidence is untrusted input and the party
> submitting it benefits from a pass. Place evidence inside explicit delimiters,
> labelled as untrusted data to be assessed and never as instruction. Validate the
> verdict against the enum; reject anything outside it. Add one adversarial
> document to the corpus containing an instruction to mark the control compliant,
> and a test asserting it does not yield `compliant`.
>
> **Provenance.** Record the criteria version (or criteria hash), the prompt
> version, and the evidence content hash on every Finding, so any verdict can be
> reproduced and explained later.
>
> Confidence below threshold sets needs_human_review rather than asserting a
> verdict. Hard max_tokens. Malformed JSON retried once, then failed cleanly with
> the instance marked for human review.
>
> System prompt constant and placed first — no variable interpolation into the
> prefix. Add a test asserting the same evidence in two different process areas
> yields the same verdict.
>
> Read the API key from `.env` via environment variable. Never hardcode it.
> FakeModelClient must keep working — tests still run without a key.
>
> Show me: one near-miss assessment with citations, the adversarial document's
> verdict, the consistency test result, and the token usage row.

---

## Slice 7 — S4 Flagging, actions, closed loop · 2 Sep

> Slice 7 only. Build S4 — flagging, routing and the resolution loop. This is the
> slice the statement most explicitly asks for and it must work end to end.
>
> Classify every non-compliant outcome into exactly one of three categories:
> **gap** (content fails criteria), **exception** (approved deviation, or a lapsed
> one), **overdue** (no evidence by due date — raised with no model call). Keep
> them distinct in the data and later in the UI.
>
> Severity from a documented formula: control severity_weight × verdict × area
> criticality × overdue duration. Deterministic, reproducible, explainable in one
> sentence.
>
> Every non-compliant finding raises an **Action** assigned to the owning team with
> a due date, moving through raised → assigned → in_progress →
> remediation_submitted → reassessed → resolved | escalated.
>
> When remediation evidence is submitted the instance re-enters S2/S3. A new
> Finding is written with supersedes_finding_id set. If it passes, the Action
> resolves with a resolution_note. Actions overdue past their own due date escalate
> on their own timer, separately from the check.
>
> Add a `reassess(check_instance_id)` entry point so remediation is re-checked on
> demand rather than waiting for the next cycle.
>
> Every transition appends an AuditEvent with the owner recorded.
>
> Show me one complete lifecycle — gap found → action raised → remediation
> submitted → re-assessed → resolved — with the full audit timeline printed.

---

## Slice 7b — Tamper-evident audit log · 2 Sep, same evening if 7 lands early

The one hardening item that shows on camera. Roughly two hours. If slice 7
overruns, defer this to Saturday, not later.

> Slice 7b only. Make the audit log tamper-evident.
>
> Each AuditEvent stores a monotonic sequence number and `prev_hash` — the hash of
> the previous event's canonical serialisation. Add `verify_chain()` which walks
> the log and returns either OK or the sequence number of the first broken link.
>
> Add two tests: an untouched log verifies clean; a log with one row edited
> directly in SQLite fails at the right sequence number.
>
> Expose verify_chain in the UI later. Do not change any other behaviour.
>
> Show me the verification passing, then failing after a deliberate tamper.

---

## Slice 8 — Evaluation harness · 4 Sep · **API key needed**

> Slice 8 only. Build the evaluation harness and produce `results.md`.
>
> Implement the baseline as a **competent** naive implementation, not a strawman:
> it skips instances with no evidence and caches identical documents by hash, but
> has no applicability rules, no pre-screen beyond that, no retrieval — it sends
> full documents plus full criteria to the same model. A reviewer will ask what
> the comparison is against; the answer must be "a reasonable implementation",
> not "the worst thing we could think of".
> **Cache baseline results to disk on first run and never re-run them.**
>
> Run both pipelines over the identical corpus and report: missed-check rate,
> simulated-manual vs automated; verdict variance for the same control across
> areas; time-to-detection of non-compliance; precision, recall and false-positive
> rate on gap detection against the truth file; share of instances resolved with
> zero model calls; tokens per audit cycle both paths with the reduction factor;
> actions raised vs resolved and mean time to resolution.
>
> For the manual baseline simulate reviewer inconsistency — the same evidence
> judged differently — so the consistency comparison means something.
>
> In `results.md`, scope every figure honestly: precision is against a synthetic
> corpus with constructed failure modes; the zero-model-call share reflects this
> corpus mix. Write those qualifiers into the file so they can't be forgotten.
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
> chronological trail (timestamp, actor, owner); a one-page method note; and the
> `verify_chain()` result.
>
> **Critical constraint: generate the pack from the audit log alone, never from
> current-state tables.** Add a test asserting the generator imports no live-state
> repository. This constraint is the entire point — it proves the trail is complete.
>
> Output as HTML or markdown that renders cleanly on screen for the video.
>
> Show me a generated pack for the full year.

Point-in-time reconstruction (`as_of` replay) is **optional**. Build it only if
this slice lands with time to spare. It is first on the cut list.

---

## Slice 9 — Dashboard · 5 Sep · **CODE FREEZE at the end**

> Slice 9 only. Build the UI — Streamlit, or FastAPI with a single HTML page.
> Whichever is fastest. This is not a frontend exercise.
>
> One screen: compliance status by process area; overdue and escalation queue;
> finding detail with **cited spans highlighted inside the source document**; open
> actions with owners, due dates and status; audit timeline for a selected check
> instance; live token and cost meter; calendar-advance control; a "run cycle now"
> button; a "re-assess" button on a check; **an evidence upload control**; a button
> to generate the audit pack; and a "verify audit chain" button showing the result.
>
> The highlighted-citation view and the upload control are the two things the video
> is built around. Make those work well and keep everything else plain and legible.
>
> Fully operable without touching a terminal.
>
> Then freeze. No features after this.

---

## Slice 10 — Video · 6–8 Sep

Not code. Script word for word against section 10 of the spec and the shot list in
`SENTINELOPS_DEMO_DESIGN.md`. Record audio separately from screen capture. Edit to
about 7 minutes.

Worth running first:

> Read CLAUDE.md and results.md. Write a 7-minute video script following section
> 10. Plain spoken English, short sentences, no marketing language. Mark which
> screen should be visible for each paragraph.

Then rewrite it in your own voice.

**Limitations section, ~20 seconds, name these yourself:** existence not
effectiveness · self-attested structured data · no independence · coverage
completeness unverified · confidence threshold uncalibrated · retention out of
scope · no segregation of duties in the prototype.

---

## If you fall behind

Cut from the top: point-in-time reconstruction · calendar-advance UI control ·
audit timeline visualisation (keep the data) · slice 7b hash chain · second
structured control · mean-time-to-resolution.

**Never cut:** citations that resolve · the truth file · the closed action loop ·
the near-miss flag · the baseline comparison · the audit pack · the dashboard ·
**the video**.

An unfinished build is the most likely way this loses. When in doubt, cut a
feature and protect the video.

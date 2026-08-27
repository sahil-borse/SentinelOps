# SentinelOps — Build Spec v2

Embi AI Nexus 2026 · Corporate Functions / Compliance · solo · video due 31 Aug 2026
SPoCs: Dipanwita Jakkula, Nancy Nithya

Claude Code implements *this*; it does not invent architecture. Save as `CLAUDE.md`.

**v2 changes:** closed-loop actions and resolutions added; exceptions promoted to
first-class; structured process data added alongside documents; owners added to
the audit trail; consistency added as a measured outcome; narrative reframed from
cost to missed checks and inconsistency.

---

## 1. The statement, and what it is actually asking for

> Compliance checks across different process areas are often manual, inconsistent,
> and dependent on teams remembering when and what needs to be reviewed. This can
> result in missed checks, delayed identification of non-compliance, and increased
> operational risk.

Six required capabilities: identify applicable checks per process area; trigger
the right check with the right team at the defined frequency; use AI to assess
available **process data or documents** against criteria; flag **gaps,
exceptions, or overdue actions**; route alerts and actions to the appropriate
team; maintain an audit trail of **checks, findings, actions, and resolutions**.

**Read the pain words: manual, inconsistent, forgotten, missed, delayed.** Cost is
never mentioned. The system's cost architecture is excellent engineering and wins
one of six criteria, but it is **not** the headline. Lead with missed checks and
inconsistency; put cost in the middle of the video.

**The three claims to make, in priority order:**

1. **Nothing is forgotten.** Applicability and scheduling are deterministic, so a
   check cannot be missed because someone didn't remember it.
2. **Every area is judged the same way.** The same control against the same
   criteria produces the same verdict regardless of who owns the area — and this
   is measured, not asserted.
3. **It closes the loop.** Finding → action → remediation → re-assessment →
   resolution, with the audit trail written as it happens.

Cost is claim four: most of a compliance engine shouldn't call a model at all.

---

## 2. Capability coverage — check this before you build

| Statement requires | Delivered by | Measured by |
|---|---|---|
| Identify applicable checks per process area | S0 Applicability | Distinct control sets per area, on camera |
| Trigger the right check, right team, right frequency | S1 Scheduling & Trigger | Missed-check rate vs simulated manual baseline |
| Assess **process data or documents** vs criteria | S3 Assessment + structured evaluator | Precision / recall / FPR vs truth file |
| Flag gaps, **exceptions**, overdue actions | S4 Flagging | All three categories present and distinct |
| Route alerts **and actions** to the right team | S4 Routing + Action lifecycle | Assignment and escalation records |
| Audit trail of checks, findings, **actions, resolutions**, **owners** | Audit log across all stages | Full timeline reconstructable per instance |
| *Expected value:* consistency across areas | Deterministic tiers + stable prompt | **Verdict variance across areas — measured** |
| *Expected outcome:* status dashboard | S5 Dashboard | Live in demo |

---

## 3. Domain model

- **ProcessArea** — `id, name, owner_team, owner_name, attributes{handles_pii,
  customer_facing, has_suppliers, region, criticality}`.
- **ControlDefinition** — `id, title, criteria_text, frequency, applies_when{},
  evidence_kind (document|structured), required_evidence_types[],
  freshness_days, severity_weight`.
- **CheckInstance** — control × area × period. `due_date, status, assigned_team,
  owner_name`.
- **Evidence** — `id, check_instance_id, kind (document|structured), doc_type,
  content, content_hash, submitted_at, author, is_remediation`.
- **Finding** — `id, check_instance_id, verdict, confidence, rationale,
  cited_spans[], gaps[], recommended_action, needs_human_review, assessed_at,
  supersedes_finding_id`.
- **Action** — **new in v2.** `id, finding_id, title, owner_team, owner_name,
  due_date, status (raised|assigned|in_progress|remediation_submitted|
  reassessed|resolved|escalated), resolution_note, resolved_at`.
- **ComplianceException** — **new in v2.** `id, control_id, process_area_id,
  rationale, approved_by, granted_at, expires_at, status (active|expired|revoked)`.
- **AuditEvent** — append-only. `ts, actor (system|ai|user), owner, action,
  entity_type, entity_id, detail`.

Two entities carry most of the v2 value: `Action` closes the loop the statement
explicitly asks for, and `ComplianceException` makes the second of its three
flag categories real rather than a boolean.

---

## 4. Architecture — five stages, closed loop

```
 calendar tick
      |
 [S0 Applicability]  zero tokens  - which controls apply where
      |
 [S1 Trigger]        zero tokens  - due, overdue, escalate, route to team
      |
 [S2 Pre-screen]     zero tokens  - missing, wrong-type, stale, unchanged, thresholds
      |                              most instances resolve here
 [S3 Assess]         model call   - verdict + citations, or structured evaluation
      |
 [S4 Flag & Route]   zero tokens  - gap / exception / overdue, severity, assignment
      |
   Action raised -> owner -> remediation evidence submitted
      |                                         |
      +------------- re-assessment -------------+
      |
   Resolved  ->  audit trail closed
```

Every transition appends an AuditEvent. The trail is a by-product of operation,
never a report generated afterwards. Say this on camera.

**S0 — Applicability (zero tokens).** Evaluate each control's `applies_when`
expression against the area's attributes. Boolean logic. Two areas with different
attributes must visibly receive different control sets.

**S1 — Trigger (zero tokens).** Generate CheckInstances from control frequency
across a simulated calendar. State machine: pending → submitted → assessed →
overdue → waived. Escalate overdue up the owner chain after N days. Route to the
assigned team by logging a notification payload. **Active ComplianceExceptions
suppress instance generation; expired ones raise an alert of their own.**

**S2 — Pre-screen (zero tokens).** Resolve everything resolvable before spending
a model call:
- No evidence → `insufficient_evidence`.
- Wrong evidence type → `insufficient_evidence`.
- Content hash unchanged since last assessed period → carry the prior finding
  forward, flagged `carried_forward`.
- Older than `freshness_days` → `gap` by rule.
- `evidence_kind == structured` with a numeric threshold → evaluate in code.

**S3 — Assess (one model call per survivor).** Chunk the document, retrieve only
the sections relevant to the criteria, never send the whole document. Strict JSON
out: `verdict (compliant|partial|gap|insufficient_evidence), confidence,
rationale, cited_spans[], gaps[], recommended_action, needs_human_review`.

`cited_spans` is mandatory — an uncited compliance verdict is a bug. Low
confidence sets `needs_human_review` rather than asserting. System prompt constant
and first, so caching hits and so **identical evidence yields identical verdicts
across areas** — this is what makes the consistency claim true.

**S4 — Flag, route, and close the loop (zero tokens).** Classify into the
statement's three categories: **gap** (content fails criteria), **exception**
(an approved deviation, or an expired one), **overdue** (no evidence by due date —
raised with no model call at all). Severity from a documented formula: control
severity weight × verdict × area criticality × overdue duration.

Every non-compliant finding raises an **Action** assigned to the owning team with
a due date. When remediation evidence arrives, the instance re-enters S2/S3, a new
Finding is written with `supersedes_finding_id` set, and if it passes, the Action
resolves. That closed loop is the strongest single beat in the demo.

---

## 5. Cost discipline

1. S0, S1, S2, S4: zero tokens, permanently.
2. Missing, wrong-type and stale evidence never reach a model.
3. Unchanged evidence reuses the prior finding via content hash.
4. Retrieve relevant sections; never send whole documents.
5. One call per assessment; batch short criteria sharing a document.
6. Stable system prompt placed first for cache hits.
7. Strict JSON, enums, hard `max_tokens`.
8. Cheap model for pre-screen classification; large model only at S3.

**Naive baseline to measure once:** every instance, every period, full document
plus full criteria to the large model, no rules, no reuse. **Cache to disk on
first run; never re-run it.**

---

## 6. What gets measured

| Metric | Why it matters |
|---|---|
| **Missed-check rate**, simulated manual vs automated | The statement's first named pain. Lead with this. |
| **Verdict variance** for the same control across areas | "Inconsistent" is the second named pain. Nobody else will measure it. |
| **Time-to-detection** of a non-compliance | "Delayed identification" — third named pain. |
| Precision / recall / false-positive rate on gap detection | Proves the assessment is real, not theatre. |
| Share of instances resolved with **zero model calls** | The cost story. |
| Tokens per audit cycle, naive vs SentinelOps | The cost story, quantified. |
| Actions raised vs resolved, mean time to resolution | Proves the loop closes. |

`TokenMeter` wraps every model call: tier, model, input/output/cached tokens,
latency, cost → SQLite. **Counts read from the response object, never estimated.**

---

## 7. Synthetic data — mandated, and it gives you ground truth

Seeded and reproducible. A fictional organisation:

- **6–8 process areas**, genuinely varied attributes so applicability differs.
- **12–15 controls** across monthly / quarterly / annual: access reviews, vendor
  due diligence, data retention, incident post-mortems, training completion,
  backup verification, supplier security attestation.
- **At least 3 controls with `evidence_kind = structured`** — training completion
  tables, backup verification logs, access review exports. The statement says
  "process data **or** documents"; show both.
- **A 12-month calendar**, so recurrence, overdue and escalation actually happen.
- Evidence of mixed quality: compliant, partial, non-compliant, stale,
  wrong-type, missing.
- **Near-miss documents** that read compliant but fail exactly one clause. Without
  these your precision figure is meaningless.
- **The same evidence submitted for the same control in two different areas**, so
  verdict consistency is measurable.
- **2–3 ComplianceExceptions**, one of which expires mid-year.
- **Remediation evidence** for several gaps, so the closed loop can be demoed.
- **Truth file** — every injected gap, which clause fails, expected verdict — in a
  path the pipeline never reads. Test that nothing under `src/` imports it.

---

## 8. Build slices — each ends in a commit that runs

| # | Slice | Target | Key? |
|---|---|---|---|
| 1 | Project, entities, SQLite, `llm/` boundary, `TokenMeter`, one end-to-end path | Aug 16 | no |
| 2 | Synthetic generator: areas, controls, calendar, document + structured evidence, near-misses, exceptions, remediation, truth file | Aug 17 | no |
| 3 | S0 applicability rules engine | Aug 18 | no |
| 4 | S1 scheduling, trigger, routing, escalation, exception suppression, audit trail with owners | Aug 20 | no |
| 5 | S2 pre-screen incl. structured threshold evaluation | Aug 21 | no |
| 6 | S3 assessment with retrieval and citations; real provider | Aug 22 | **yes** |
| 7 | S4 flagging, severity, Action lifecycle, remediation re-assessment loop | Aug 23 | yes |
| 8 | Evaluation harness: baseline, all seven metrics, `results.md` | Aug 24 | **yes** |
| 9 | Dashboard | Aug 26 | no |
| — | **CODE FREEZE** | **Aug 26** | |
| 10 | Script, record, edit video | Aug 27–30 | |
| 11 | Submit | Aug 31 am | |

Slices 1–5 need no API key. Build them while credits are pending.

---

## 9. Dashboard — the Expected Outcome names it explicitly

One screen: compliance status by process area; overdue and escalation queue;
finding detail with **cited spans highlighted inside the source document**; open
actions with owners and due dates; audit timeline per check instance; live token
and cost meter; calendar-advance control.

The highlighted-citation view is the shot the video is built around. Make that one
look good; keep everything else plain.

---

## 10. Video — cap 10 min, target 7

1. **0:00–1:15 The problem, concretely.** A quarterly access review nobody
   remembered, found four months later in an audit. Two areas that ran the same
   check and reached different conclusions. Name the operational risk.
2. **1:15–2:15 Architecture and data flow.** The five stages, one diagram,
   explained once. The guidelines explicitly ask for this.
3. **2:15–5:00 Demo.** Advance the calendar: checks generate per area — visibly
   *different* checks — route to teams, go overdue, escalate. A compliant document
   passes. **A near-miss is flagged with the failing clause highlighted.** A
   structured data check evaluates with no model call. An expired exception raises
   an alert. An Action is raised, remediation evidence submitted, re-assessed, and
   **resolved** — with the audit trail assembling itself throughout.
4. **5:00–5:45 AI capability.** Which model where and why. Why scheduling and
   applicability deliberately never touch a model. How citations and the
   human-review flag keep every decision auditable.
5. **5:45–6:30 Numbers.** Missed-check rate, verdict consistency, time-to-detection,
   precision/recall — then tokens and cost.
6. **6:30–7:00 Business value, limitations, next steps.** Named by you first.

Script word for word. Record audio separately from screen capture.

---

## 11. Non-goals

No auth, no user management, no Postgres, no Docker, no real integrations, no
email sending (log the payload), no multi-tenancy, no policy-authoring UI, no
agent loop. Every hour here is an hour not spent on the video.

---

## 12. Rules of engagement

- Stuck 90 minutes → stub it, commit, note it in `STUBS.md`, move on.
- Read the diff on every commit; be able to explain every file.
- If a change makes the section 4 diagram harder to draw on one slide, don't.
- Maintain `PROGRESS.md`: one line per completed slice.

## 13. Cut list, if behind

Cut from the top: calendar-advance UI control (script it instead) · audit timeline
visualisation (keep the data) · the second structured control · mean-time-to-
resolution metric.

**Never cut:** citations, the truth file, the closed action loop, the near-miss
flag, the baseline comparison, the dashboard, the video.

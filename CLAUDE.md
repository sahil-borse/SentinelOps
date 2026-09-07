# SentinelOps — Build Spec v3

Team Transformers · Embi AI Nexus 2026 · solo · video due 9 Sep 2026
Corporate Functions – Compliance – Intelligent Compliance Monitoring and Trigger System

**Save as `CLAUDE.md`.** This supersedes v2. Written after two rounds of
clarification with the compliance stakeholder; where it differs from earlier
documents, this wins.

---

## 1. What the system is

A **findings-management and closure-tracking system** for compliance gaps, plus a
**scheduling engine** for periodic compliance obligations.

Two scheduled things, easily confused, kept separate:

| | **Audits** | **Compliance activities** |
|---|---|---|
| Who acts | PA/InfoSec auditor | The auditable unit's owner |
| What it is | Internal Audit, QAREV, Release Audit, document review | Risk register review, manual/guideline update, audit readiness, controlled document review |
| Output | **Findings** | Evidence of completion |
| Cadence | Scheduled programme | Defined frequency (monthly, quarterly, annual) |

**Findings are children of audits.** They may also arise from a compliance
activity whose evidence fails assessment, or be raised standalone.

### Ground truth from the stakeholder

- Gaps are identified by the **PA/InfoSec team** during scheduled Internal Audits,
  QAREVs, Release Audits and document reviews.
- Evidence is submitted by support functions (IT, Admin, Purchase, HR and others)
  and may be policy or procedure updates, updated reports or trackers, or records
  showing an action was completed.
- **Severity is assigned by the auditor**, finalised after the audit completes, and
  communicated to the auditee in the audit report, typically by email.
- If evidence is insufficient, PA/InfoSec **communicate the gaps and request
  revised evidence. The finding remains Open until the auditor is fully
  satisfied.** Only then is it formally closed.
- **Recurring** means the same *type* of gap occurring again in a different area,
  project, or period.
- Escalation timing depends on severity and priority: 3–4 days for urgent cases,
  1–2 weeks otherwise, **maximum one week to escalation preferred**.
- Scale: **roughly 6 support functions, 15–18 findings open at any time.**
- Auditable units are not only support functions — a project team, IT, HR, Finance
  all qualify. Model the subject generically.
- **No standard gap taxonomy exists.** The auditor describes each gap in their own
  words.
- **An automatically generated audit report is wanted.**

### What this means for the pitch

At 15–18 open findings this is **not a throughput problem.** Never claim scale.
The value is **consistency, institutional memory, and relentless follow-up** — a
system that never forgets to chase, and that notices this month's gap in Finance
resembles one raised against a project team eight months ago. No human holds that
comparison across 18 months, six functions and several project teams.

---

## 2. Where AI is used, and where it is not

Five uses, each justified. Everything else is deterministic.

| # | AI use | Why a model | Human authority |
|---|---|---|---|
| 1 | **Classify gap type** from the auditor's free-text description | No taxonomy exists; this is genuine language work | Auditor may override the category |
| 2 | **Detect recurrence** — same gap type, different area, project or period | Requires semantic similarity across 18 months of free text | Surfaced as a suggestion with prior finding ids |
| 3 | **Evaluate submitted evidence** against the finding and its required action, with resolvable citations | Reading a document against a requirement | **Auditor decides closure. Always.** |
| 4 | **Suggest severity** at audit completion | Pattern from description and context | **Auditor assigns. The suggestion is advisory only.** |
| 5 | **Prioritisation brief** — one call per cycle over ranked findings and metrics | Synthesis across the portfolio | Advisory; changes no state |

Plus **audit report drafting** (§6), which is generation over structured data.

**Never AI:** scheduling, applicability, due dates, reminder and escalation timing,
status transitions, closure decisions, permission checks, analytics.

---

## 3. Domain model

- **AuditableUnit** — `id, name, kind (support_function | project_team |
  department), owner_identity, attributes{handles_pii, customer_facing,
  has_suppliers, region, criticality}`. Six support functions plus several project
  teams.
- **Identity** — `id, name, role (pa_infosec | unit_owner | management),
  auditable_unit (nullable), reports_to (nullable)`.
- **AuditProgramme / ScheduledAudit** — `id, kind (internal_audit | qarev |
  release_audit | document_review), scope (units), auditor_identity,
  planned_date, conducted_date, status (planned | in_progress | completed),
  report_generated_at`.
- **ControlDefinition** — a periodic compliance obligation: `id, title,
  criteria_text, frequency, applies_when{}, evidence_kind (document | structured),
  required_evidence_types[], freshness_days`. Titles are the activities the
  stakeholder named: periodic risk register review · internal audit readiness ·
  external audit readiness · process manual and guideline review · controlled
  document review · closure and validation of prior audit findings · review of
  newly introduced or changed processes · security awareness training completion ·
  access review · vendor and supplier due diligence · incident post-mortem
  completion · backup and restore verification · data retention review · business
  continuity test.
- **CheckInstance** — one control × unit × period. The compliance-activity track.
- **Finding** — the central tracked object.
  `id, source (audit | activity_assessment | self_identified), audit_id (nullable),
  check_instance_id (nullable), auditable_unit_id, description (auditor's own
  words), gap_category (AI-classified, auditor-overridable),
  severity (Major | Minor | Observation, auditor-assigned),
  suggested_severity (AI, advisory), raised_by, raised_at, owner_identity,
  agreed_action_plan, target_date, status, follow_up_count, recurrence_of[],
  closed_by, closed_at, closure_remarks`.
- **EvidenceSubmission** — one round. `id, finding_id, round_number, submitted_by,
  submitted_at, evidence_ref, owner_note, auditor_response (pending | accepted |
  insufficient), auditor_remarks, responded_by, responded_at`.
- **Evidence** — write-once. `id, kind, doc_type, content, content_hash,
  submitted_at, author`.
- **Assessment** — an AI verdict on an evidence submission. Immutable.
  `id, submission_id, verdict, confidence, rationale, cited_spans[], gaps[],
  needs_human_review, criteria_version, prompt_version, evidence_hash,
  supersedes_assessment_id`.
- **ComplianceException** — approved deviation with rationale, approver, expiry.
- **Notification** — `id, recipient_identity, kind, subject, body, sent_at,
  related_entity, escalation_level, read_at`.
- **AuditEvent** — append-only, hash-chained. `seq, prev_hash, entry_hash, ts
  (simulated), actor_identity, actor_kind (system | ai | user), owner, action,
  entity_type, entity_id, detail`.

---

## 4. Finding lifecycle — as the stakeholder described it

**Authoritative status is binary: Open or Closed.** A finding remains Open until
the auditor is satisfied. Owner progress is self-reported and advisory — it never
moves the authoritative state.

```
 Audit conducted
      ↓
 Finding raised (auditor: description, severity, owner, action plan, target date)
      ↓
 OPEN ──────────────────────────────────────────────────────┐
      │                                                     │
      │  owner sets progress: acknowledged →                │
      │  action_in_progress → implemented   (advisory)      │
      │                                                     │
      │  owner submits evidence  ── round N ──┐             │
      │                                       ↓             │
      │                          auditor reviews (AI assists)
      │                                       │             │
      │              insufficient ────────────┘             │
      │              (remarks returned, round N+1 expected;  │
      │               finding stays OPEN, follow_up_count++) │
      │                                                     │
      │              accepted ──────────────────────────────┤
      ↓                                                     ↓
   reminders + escalation running throughout            CLOSED
                                                (auditor only, with remarks)
```

Two independent clocks run on every open finding: the **reminder cadence** and the
**escalation timer**. Both are severity-driven (§5).

---

## 5. Reminders and escalation

Deterministic, severity-driven, configurable:

| Severity | Default target | First reminder | Escalation |
|---|---|---|---|
| Major (urgent) | 3–4 days | 1 day before target | 1 day past target |
| Major | 1 week | 2 days before | 3 days past target |
| Minor | 2 weeks | 3 days before | 5 days past target |
| Observation | 2–4 weeks | 5 days before | 7 days past target |

**Maximum one week from target date to escalation** in every case — the
stakeholder's stated preference. Escalation goes to the owner's `reports_to` and
to PA/InfoSec, at increasing levels. Reminders continue after escalation; they are
not replaced by it. `follow_up_count` increments on every reminder **and** on every
insufficient-evidence round.

---

## 6. Audit report generation

Confirmed as wanted. At audit completion, generate the report currently written
and emailed by hand: audit kind, scope, auditor, dates, and every finding with its
description, category, severity, owner, agreed action plan and target date — plus
any recurrence links to prior findings.

Draft the narrative summary with one model call over the structured findings; every
statement in it must cite finding ids. The auditor reviews and confirms before it
is issued; issuing appends an audit event.

This replaces a real manual step and costs almost nothing, since the data is
already structured.

---

## 7. Segregation of duties — enforced and tested

| Action | pa_infosec | unit_owner | management |
|---|---|---|---|
| Conduct audit, raise finding, assign severity | ✔ | ✘ | ✘ |
| Set owner progress, submit evidence | ✘ | ✔ (own unit only) | ✘ |
| Respond to a submission (accept / insufficient) | ✔ | ✘ | ✘ |
| **Close a finding** | ✔ | ✘ | ✘ |
| View escalations and portfolio trend | ✔ | own unit | ✔ |

The identity that submitted evidence may never be the identity that accepts it or
closes the finding. Both blocked paths have tests. In the UI the owner's Close
control is **absent, not disabled**.

---

## 8. Analytics

Deterministic, computed from state and the audit log:

- Open vs closed — count **and percentage**, overall and per unit.
- Severity mix: Major / Minor / Observation, per unit.
- Overdue findings with **ageing**, bucketed (0–30, 31–60, 61–90, 90+ days).
- Findings by auditable unit, by gap category, by audit kind.
- **Recurring findings** — same gap category in a different unit, project or period.
- Findings requiring **multiple evidence rounds or multiple reminders**, with the
  distribution.
- **Trend over time** — open finding count by month across the corpus window.
- Closure performance — mean and median days from raise to closure, by severity.
- Upcoming audits and compliance activities due in the next 30 days.

---

## 9. Cost discipline

Still correct engineering, but **demoted in the pitch** — at this volume, cost is
not the story. Keep the meter running and let it speak for itself.

Deterministic everywhere except the five uses in §2. Evidence pre-screen resolves
missing, wrong-type, stale and unchanged submissions before any model call. Strict
JSON, hard `max_tokens`, constant system prompt placed first. One prioritisation
call per cycle, not per finding. Token counts read from the response object, never
estimated.

---

## 10. Data

Synthetic, seeded, reproducible. **Realistic volume, not inflated:** 6 support
functions plus 3–4 project teams; 18 months; roughly 80–100 findings total with
15–18 open at the "today" mark. Include: audits of all four kinds; findings across
all three severities; several needing 3+ evidence rounds; at least two recurring
gap-category sets spanning different units and periods; near-miss evidence; one
adversarial injection document; exceptions including one that lapses; and an
isolated truth file the pipeline never reads.

---

## 11. Non-goals

No auth or user management — the role switcher is an identity selector. No real
email. No Postgres, Docker or multi-tenancy. No agent loop. No live integrations.

---

## 12. Rules of engagement

- One slice per session. Never build ahead.
- 90 minutes stuck → stub it, note in `STUBS.md`, commit, move on.
- Read every file list; be able to explain any file. AI Day is live.
- Audit trail is a by-product, written as things happen, and hash-chained.
- Simulated business time on every audit event and notification — never wall-clock.
- If a change makes the §4 lifecycle harder to draw on one slide, don't make it.

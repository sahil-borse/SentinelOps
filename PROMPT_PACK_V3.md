# SentinelOps — Prompt Pack v3

Slices 10–19, realigning the build to the stakeholder's confirmed process.
**Evolving the existing repo.** Save `SPEC_V3.md` as `CLAUDE.md` first, replacing v2.

Repo `D:\projects\SentinelOps` · Python 3.11.9 · slices 1–9 built.

---

## Session ritual

**Open:** *Re-read CLAUDE.md and PROGRESS.md. State which slice we are on and what
exists, then implement only that slice.*

**Close:** *List every file created or changed with one line each. Run the tests.
Append one line to PROGRESS.md.*

Then commit. 90 minutes stuck → stub, note in `STUBS.md`, commit, move on.

---

## Slice 10 — Domain model v3

The invasive one. Do it first, cleanly, and report before you cut.

> Slice 10 only. This is a refactor. **Before writing code, report the blast
> radius:** how many modules reference `Finding`, `Action` and `CheckInstance`, and
> whether this is contained or entangled. If it is larger than expected, stop and
> tell me.
>
> Then restructure to the model in CLAUDE.md §3:
>
> - `ProcessArea` → **`AuditableUnit`** with a `kind` of support_function,
>   project_team or department. Findings can be raised against any of them.
> - Add **`Identity`** — name, role (pa_infosec | unit_owner | management),
>   auditable_unit (nullable), reports_to (nullable).
> - Add **`ScheduledAudit`** — kind (internal_audit | qarev | release_audit |
>   document_review), scope, auditor, planned and conducted dates, status.
> - Existing `Finding` → **`Assessment`** (an immutable AI verdict on a submission,
>   keeping citations, confidence, criteria and prompt versions, evidence hash).
> - Existing `Action` → **`Finding`**, now the central tracked object with the
>   fields in §3. Its links to audit and check instance are both **nullable**.
> - Add **`EvidenceSubmission`** — a round: finding, round_number, submitted_by,
>   evidence, owner_note, auditor_response, auditor_remarks, responded_by.
> - Audit events reference an `Identity` rather than an actor string, keeping
>   actor_kind alongside.
>
> Keep `CheckInstance` — it remains the periodic compliance-activity track, which
> is separate from audits.
>
> Update every test. Run `verify_chain()` after migration and show it clean.
>
> Show me the blast-radius report first, then the migrated model and a green suite.

---

## Slice 11 — Corpus v3

> Slice 11 only. Rebuild the synthetic corpus at **realistic volume** — the
> stakeholder runs roughly 6 support functions with 15–18 findings open at a time.
> Do not inflate it.
>
> Generate 6 support functions (IT, Admin, Purchase, HR, Finance, Facilities) plus
> 3–4 project teams, each with a named owner identity, plus 2 PA/InfoSec auditors
> and 2 managers with reporting lines.
>
> Rename the control library to the activities in CLAUDE.md §3 — risk register
> review, audit readiness, process manual review, controlled document review,
> closure of prior findings, review of changed processes, and the rest.
>
> **18 months, Jan 2026 to Jun 2027, with a defined "today" partway through.**
>
> Generate scheduled audits of all four kinds across the window, each producing
> 2–6 findings written in an auditor's own words — free text, no category label,
> because no taxonomy exists.
>
> Roughly 80–100 findings total, 15–18 open at "today". Severity spread across
> Major, Minor and Observation. Include: several findings needing 3+ evidence
> rounds before acceptance; at least two **recurring gap sets** — the same kind of
> gap described differently, in different units and different periods; a spread of
> ageing; near-miss evidence; one adversarial injection document; exceptions
> including one that lapses.
>
> Update the isolated truth file — recorded gaps, expected verdicts, **and the
> intended recurrence groupings**, so recurrence detection can be scored. Keep the
> isolation test.
>
> Show me: findings by source, severity, status; the recurrence sets; the evidence
> round distribution; and the open count at "today".

---

## Slice 12 — Finding lifecycle, evidence rounds, segregation of duties

> Slice 12 only. Implement the lifecycle in CLAUDE.md §4 exactly as the stakeholder
> described it.
>
> **Authoritative status is Open or Closed.** A finding stays Open until a
> pa_infosec identity closes it. The owner's progress — acknowledged, action in
> progress, implemented — is **self-reported and advisory** and stored separately;
> it never moves the authoritative status.
>
> **Evidence rounds.** The owner submits evidence as a numbered round. The auditor
> responds `accepted` or `insufficient` with remarks. Insufficient keeps the
> finding Open, increments `follow_up_count`, and expects a further round.
> Accepted allows closure.
>
> **Closure** is by a pa_infosec identity only, recording closed_by, closed_at and
> closure_remarks.
>
> **Segregation of duties per CLAUDE.md §7, enforced and tested:** only pa_infosec
> raises findings, assigns severity, responds to submissions and closes. Only a
> unit_owner submits evidence, and only for their own unit. The identity that
> submitted evidence may never accept it or close the finding. A test for each
> blocked path.
>
> Severity is **auditor-assigned**, finalised at audit completion. Store
> `suggested_severity` separately for the AI suggestion added in slice 14 —
> advisory only, never authoritative.
>
> Every transition appends an audit event with the acting identity and remarks.
>
> Show me one finding through three evidence rounds — two insufficient, one
> accepted, then closed — with the full trail, and two blocked attempts.

---

## Slice 13 — Reminders, escalation, notifications

> Slice 13 only. Make notifications first-class records, not logged payloads.
>
> `Notification`: recipient_identity, kind (audit_due | activity_due |
> finding_raised | reminder | evidence_requested | overdue | escalation |
> evidence_submitted | closure | exception_lapsed), subject, body, sent_at,
> related_entity, escalation_level, read_at. Persisted and queryable per identity —
> this becomes the per-role inbox.
>
> **Severity-driven timing per CLAUDE.md §5.** Major/urgent targets 3–4 days with
> escalation one day past; Minor two weeks with escalation five days past;
> Observation longer. **Never more than one week from target date to escalation** —
> that is the stakeholder's stated preference. Make the table configurable in one
> place and printable.
>
> Reminders run on their own cadence and continue after escalation. Escalation goes
> to the owner's `reports_to` and to PA/InfoSec at increasing levels.
> `follow_up_count` increments on every reminder **and** every insufficient round.
>
> PA/InfoSec are notified on every status change, evidence submission, overdue
> action and closure request — not only the owning unit.
>
> Nothing is actually sent. Zero model calls — assert it.
>
> Show me the notification history for one finding that took three reminders and an
> escalation, listed per recipient, with the simulated timestamps.

---

## Slice 14 — The AI layer

The five uses from CLAUDE.md §2. This is where the AI value lives.

> Slice 14 only. Four model-backed capabilities, each with human authority intact.
>
> **1. Gap classification.** The auditor writes the finding in free text and no
> taxonomy exists. Classify each into a `gap_category` — derive a working set of
> categories from the corpus rather than hardcoding a list, then classify
> consistently against it. The auditor may override; the override is recorded.
>
> **2. Recurrence detection.** Using gap_category plus semantic similarity of the
> descriptions, find findings that represent the same type of gap in a **different
> unit, project or period**. Populate `recurrence_of` with prior finding ids.
> Score this against the recurrence groupings in the truth file and report
> precision and recall — this is the capability no human can perform across 18
> months, and it must be measured, not asserted.
>
> **3. Evidence evaluation.** When a round is submitted, assess it against the
> finding description and the agreed action plan. Strict JSON: verdict, confidence,
> rationale, cited_spans, gaps, needs_human_review. **Every cited span must resolve
> to text that actually appears in the evidence — verify it, and fail the
> assessment if it does not.** The result is a recommendation shown to the auditor.
> **The auditor decides. Always.**
>
> **4. Severity suggestion** at audit completion, written to `suggested_severity`.
> Advisory. The auditor's assignment is authoritative and the two are stored
> separately so divergence is visible.
>
> **Prompt injection defence:** evidence is untrusted input submitted by the party
> who benefits from acceptance. Delimit it explicitly as data, never instruction.
> Validate verdicts against the enum. Keep the adversarial corpus document and a
> test asserting it does not yield `accepted`.
>
> Batch classification; one call per submission for evaluation. Constant system
> prompt placed first. FakeModelClient must keep working.
>
> Show me: the derived categories, the recurrence precision and recall against the
> truth file, one evidence evaluation with resolving citations, and the adversarial
> document's result.

---

## Slice 15 — Analytics

> Slice 15 only. Build every metric in CLAUDE.md §8, deterministically, from state
> and the audit log.
>
> Open vs closed count and percentage, overall and per unit · severity mix per unit
> · overdue with ageing bucketed 0–30 / 31–60 / 61–90 / 90+ · findings by unit, by
> gap category, by audit kind · recurring findings across units and periods ·
> findings needing multiple evidence rounds or multiple reminders, with
> distributions · open findings by month across the 18-month window with a rising
> or falling verdict · closure performance, mean and median days by severity ·
> upcoming audits and activities due in 30 days.
>
> Tests must detect the seeded patterns from slice 11 — the recurrence sets and the
> multi-round findings.
>
> Show me the full metric set printed for the corpus at "today".

---

## Slice 16 — Prioritisation brief and audit report

> Slice 16 only. Two generated artifacts.
>
> **Prioritisation brief.** First a deterministic priority score per open finding:
> unit criticality, severity, days to or past target, recurrence count, follow-up
> count. Documented and printable formula. Then **one model call per cycle** over
> the ranked list plus the slice 15 metrics, producing strict JSON:
> `top_priorities` (finding ids with one-line reasons), `emerging_patterns`,
> `recommended_focus`. Every claim cites finding ids or a named metric; an uncited
> claim is rejected by test. Advisory — it changes no state.
>
> **Audit report.** The stakeholder confirmed this is wanted; today it is written
> and emailed by hand. At audit completion generate a report containing the audit
> kind, scope, auditor, dates, and every finding with description, category,
> severity, owner, agreed action plan, target date, and any recurrence links to
> prior findings. One model call drafts the narrative summary; every statement in
> it cites finding ids. The auditor confirms before issue, and issuing appends an
> audit event.
>
> Render both as clean HTML or markdown for the video.
>
> Show me a generated brief with citations, a generated audit report, and the token
> cost of one cycle.

---

## Slice 17 — Dashboard and role switcher

> Slice 17 only. Rebuild the dashboard. This is the screen the video is built
> around — it must read as a compliance team's morning screen, not an engineering
> demo.
>
> **Role switcher** in the header: an identity selector, not an auth system. No
> login, no passwords, no sessions. Selecting an identity changes both the view and
> the permitted actions.
>
> **PA/InfoSec view** — the prioritisation brief at the top; open vs closed with
> percentages; severity mix; overdue with ageing; findings by unit; **recurring
> findings with their prior occurrences**; multi-round findings; trend over time;
> upcoming audits and activities; the review queue of submissions awaiting
> response; their notification inbox.
>
> **Unit owner view** — only their unit's findings; their queue by target date;
> evidence upload; self-reported progress controls. **No Close control and no
> Accept control — visibly absent, not disabled.** Their inbox showing the
> reminders they received.
>
> **Management view** — escalated findings, unit-level trend, ageing summary.
>
> Retain: finding detail with **cited spans highlighted inside the source
> document**, the audit timeline for any finding, the token and cost meter, the
> audit pack button, verify-chain.
>
> Fully operable without a terminal.
>
> Show me all three views and confirm the owner cannot see a Close control.

---

## Slice 18 — Demo instrumentation

> Slice 18 only.
>
> **Jump to next event** — advance the simulated clock to the next meaningful
> moment (reminder due, target date reached, escalation triggered, audit due),
> naming what the next event is before jumping. Not fixed increments.
>
> **Scenario reset** — restore the exact seeded state in one click so every
> recording take starts identically.
>
> **Simulated time everywhere** — assert no audit event or notification generated
> during a simulated run carries a wall-clock date. This regressed once before.
>
> Show me a jump sequence through one finding's reminder and escalation timeline,
> and a reset returning to the exact initial state.

---

## Slice 19 — Real provider run and freeze

> Slice 19 only. No new features.
>
> Run the full pipeline against the real provider. Run the competent baseline once
> and cache it — it skips missing evidence and caches identical documents, but has
> no applicability rules, no pre-screen, no retrieval.
>
> Regenerate `results.md` with every figure scoped honestly: precision against a
> synthetic corpus with constructed failure modes; recurrence precision and recall
> against the seeded groupings; the baseline described as a reasonable
> implementation. **State the volume — roughly 90 findings over 18 months — and do
> not claim throughput benefits.**
>
> Regenerate the audit evidence pack from the real run, still built from the audit
> log alone, with `verify_chain()` inside it.
>
> Run the full demo path end to end in the UI and report anything that stumbles.
>
> Then freeze.

---

## Video: what changed

- **Open on the chase, not the calendar.** A Major finding raised in an internal
  audit in March, evidence returned twice as insufficient, four reminders, closed
  in August — and nobody could say from memory whether a similar gap had been
  raised before.
- **The strongest moment is now recurrence.** *"This gap in Finance is the same
  type raised against a project team eight months ago, and against IT before
  that."* Nobody holds that in their head. Lead the AI section with it.
- **Second: the role switch.** The owner's Close button is absent, not disabled.
- **Third: the reminder inbox** — three reminders and an escalation nobody wrote.
- Then evidence evaluation with resolving citations, the adversarial document
  failing, the generated audit report, the audit pack, the tamper demo.
- **Never claim scale.** 15–18 open findings. The value is memory and consistency.
- End on limitations, in your own voice.

---

## Cut list

From the top: management view · closure performance percentiles · jump-to-next-event
· severity suggestion · `emerging_patterns` in the brief · trend reconstruction
from the log (compute from current state).

**Never cut:** recurrence detection and its measured score · segregation of duties
with the absent Close control · evidence rounds and follow-up counts · the
auditor-closes rule · the dashboard · the audit report · **the video**.

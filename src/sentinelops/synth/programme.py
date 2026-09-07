"""The audit programme — the other scheduled thing, and its findings.

Section 1 keeps audits and compliance activities apart, and the corpus has to as
well or the distinction is only a paragraph in a document. So the generator now
carries a programme: eight audits across the eighteen months, covering all four
kinds the stakeholder named, with findings raised under them in the auditor's
own words.

The descriptions are written the way an auditor writes them — free text, no
shared vocabulary, the same underlying problem described differently in
different units. That is not colour. Section 2 justifies the gap-classification
model on exactly this basis ("no standard gap taxonomy exists; the auditor
describes each gap in their own words"), and a corpus whose descriptions were
drawn from a fixed list would make that model look far better than it is.

Two of the sets here recur on purpose: privileged access left with leavers, and
supplier records that were never completed. They appear in different units,
months apart, phrased differently each time — which is the comparison section 2
says no human holds across eighteen months and six functions.
"""

from __future__ import annotations

from datetime import date

#: (id, kind, planned, conducted, auditor, scope, title)
AUDIT_PROGRAMME: list[tuple] = [
    ("AUD-IA-2026-H1", "internal_audit", date(2026, 3, 9), date(2026, 3, 20),
     "ID-PA-KAUR",
     ["AREA-CUSTOPS", "AREA-PAYMENTS", "AREA-HR"],
     "Internal Audit — H1 2026, customer-facing functions"),
    ("AUD-QA-2026-Q2", "qarev", date(2026, 5, 11), date(2026, 5, 22),
     "ID-PA-OSEI",
     ["AREA-PLATFORM", "AREA-PRJ-ATLAS"],
     "QAREV — platform and Project Atlas"),
    ("AUD-REL-2026-07", "release_audit", date(2026, 7, 6), date(2026, 7, 10),
     "ID-PA-KAUR",
     ["AREA-PRJ-ATLAS", "AREA-PRJ-BEACON"],
     "Release Audit — Atlas 2.0 and Beacon pilot"),
    ("AUD-DOC-2026-09", "document_review", date(2026, 9, 7), date(2026, 9, 18),
     "ID-PA-OSEI",
     ["AREA-PROC", "AREA-FINREP", "AREA-ITSVC"],
     "Controlled document review — procurement and finance"),
    ("AUD-IA-2026-H2", "internal_audit", date(2026, 11, 2), date(2026, 11, 13),
     "ID-PA-KAUR",
     ["AREA-ITSVC", "AREA-MKTG", "AREA-PRJ-CORAL"],
     "Internal Audit — H2 2026, IT services and marketing"),
    ("AUD-QA-2027-Q1", "qarev", date(2027, 2, 8), date(2027, 2, 19),
     "ID-PA-OSEI",
     ["AREA-PAYMENTS", "AREA-PRJ-BEACON"],
     "QAREV — payments and Project Beacon"),
    ("AUD-REL-2027-04", "release_audit", date(2027, 4, 5), date(2027, 4, 9),
     "ID-PA-KAUR",
     ["AREA-PRJ-CORAL", "AREA-PLATFORM"],
     "Release Audit — Coral first release"),
    # Planned but not yet conducted at the vantage point: the upcoming-audits
    # panel needs something genuinely upcoming, and "everything in the programme
    # has already happened" is not what an audit calendar ever looks like.
    ("AUD-DOC-2027-10", "document_review", date(2027, 10, 12), None,
     "ID-PA-OSEI",
     ["AREA-CUSTOPS", "AREA-HR"],
     "Controlled document review — customer operations and HR"),
]

#: (audit_id, unit_id, severity, description, agreed action plan)
#:
#: Severities are spread across all three deliberately, and the phrasing varies
#: even where the underlying gap is the same — see the module docstring.
AUDIT_FINDINGS: list[tuple[str, str, str, str, str]] = [
    # --- AUD-IA-2026-H1 ------------------------------------------------------
    ("AUD-IA-2026-H1", "AREA-PAYMENTS", "Major",
     "Three staff who left the payments team in January still held privileged "
     "access to the settlement console at the time of the audit. The joiners-"
     "movers-leavers checklist was completed but the access revocation step was "
     "not evidenced for any of the three.",
     "Revoke the three accounts, and add a monthly reconciliation between HR "
     "leaver records and privileged access holders."),
    ("AUD-IA-2026-H1", "AREA-CUSTOPS", "Minor",
     "The complaints register is maintained but was last reconciled against the "
     "ticketing system in October. Two complaints logged in the ticketing system "
     "in February do not appear in the register.",
     "Reconcile the register monthly and backfill the two missing entries."),
    ("AUD-IA-2026-H1", "AREA-HR", "Observation",
     "Security awareness training completion is tracked in a spreadsheet that "
     "several people can edit without any record of who changed what. No "
     "discrepancy was found, but the tracker cannot be relied on as evidence.",
     "Move the tracker to the LMS export, or restrict edit rights and enable "
     "version history."),
    # --- AUD-QA-2026-Q2 ------------------------------------------------------
    ("AUD-QA-2026-Q2", "AREA-PLATFORM", "Major",
     "Backup restore verification for the primary datastore has been recorded as "
     "'passed' each month, but the team could not produce the restore logs for "
     "March or April. The verification appears to have been signed off without "
     "the test being run.",
     "Re-run the restore test for both months and retain the logs with the "
     "sign-off."),
    ("AUD-QA-2026-Q2", "AREA-PRJ-ATLAS", "Minor",
     "Project Atlas has no entry in the risk register despite handling customer "
     "personal data. The project was stood up in February and the register was "
     "last reviewed in January.",
     "Add Atlas to the register and bring forward the next review."),
    # --- AUD-REL-2026-07 -----------------------------------------------------
    ("AUD-REL-2026-07", "AREA-PRJ-ATLAS", "Major",
     "The Atlas 2.0 release went to production without the pre-release security "
     "review being completed. The review was scheduled and then skipped when the "
     "release date moved forward; no exception was raised.",
     "Complete the review retrospectively and make it a release gate that cannot "
     "be skipped without a recorded exception."),
    ("AUD-REL-2026-07", "AREA-PRJ-BEACON", "Observation",
     "Beacon's change log records what was deployed but not who approved it. No "
     "unapproved change was identified.",
     "Record the approver against each change."),
    # --- AUD-DOC-2026-09 -----------------------------------------------------
    ("AUD-DOC-2026-09", "AREA-PROC", "Major",
     "Due diligence files for two suppliers onboarded in Q2 contain no financial "
     "standing check and no signed information security schedule. Both suppliers "
     "have access to internal systems.",
     "Complete both files, and block supplier activation until due diligence is "
     "signed off."),
    ("AUD-DOC-2026-09", "AREA-FINREP", "Minor",
     "The financial reporting process manual is two versions behind the process "
     "actually followed. The quarterly close steps were changed in March and the "
     "manual still describes the old sequence.",
     "Update the manual and align the review cycle to the process change log."),
    ("AUD-DOC-2026-09", "AREA-ITSVC", "Minor",
     "Four controlled documents are past their review date, the oldest by seven "
     "months. All four are still in active use.",
     "Review all four and set calendar reminders ahead of the review dates."),
    # --- AUD-IA-2026-H2 ------------------------------------------------------
    ("AUD-IA-2026-H2", "AREA-ITSVC", "Major",
     "Contractors whose engagements ended in August and September retained "
     "active accounts and VPN access. Four accounts were still enabled at the "
     "time of the audit, one of them used after the engagement end date.",
     "Disable all four immediately and tie account expiry to the contract end "
     "date in the joiners-movers-leavers process."),
    ("AUD-IA-2026-H2", "AREA-MKTG", "Observation",
     "Marketing holds a campaign list containing personal data with no retention "
     "period recorded against it. The data is in scope of the retention policy.",
     "Record a retention period and schedule the first deletion run."),
    ("AUD-IA-2026-H2", "AREA-PRJ-CORAL", "Minor",
     "Coral's data protection impact assessment was drafted but never approved. "
     "It has sat in draft since the project started.",
     "Complete and approve the DPIA before the first release."),
    # --- AUD-QA-2027-Q1 ------------------------------------------------------
    ("AUD-QA-2027-Q1", "AREA-PAYMENTS", "Major",
     "A third-party integration partner's access to the payments API remained "
     "enabled five months after the engagement closed. The access was not used, "
     "but nobody had reviewed it.",
     "Revoke the access and add third-party credentials to the quarterly access "
     "review scope."),
    ("AUD-QA-2027-Q1", "AREA-PRJ-BEACON", "Minor",
     "Beacon's supplier records are incomplete: the security questionnaire is "
     "missing for one of the three suppliers the project uses directly.",
     "Obtain the questionnaire, or route the supplier through procurement."),
    # --- AUD-REL-2027-04 -----------------------------------------------------
    ("AUD-REL-2027-04", "AREA-PRJ-CORAL", "Major",
     "The Coral release shipped with a database account whose password had not "
     "been rotated since the project began, and which is shared between two "
     "services.",
     "Rotate the credential, split it per service, and bring both into the key "
     "rotation schedule."),
    ("AUD-REL-2027-04", "AREA-PLATFORM", "Observation",
     "Post-incident reviews are completed but the actions arising from them are "
     "tracked in the incident ticket rather than anywhere that survives the "
     "ticket being closed.",
     "Track post-incident actions in the same place as audit findings."),
]

#: Which of the above an auditor later closed, and with what remarks. Left as
#: data rather than derived, because "the auditor was satisfied" is a decision
#: and a corpus that invents those wholesale is describing a system where
#: closure is automatic — the exact opposite of what section 4 says.
AUDIT_CLOSURES: list[tuple[str, int, str]] = [
    # (audit_id, index within that audit's findings, days after raising)
    ("AUD-IA-2026-H1", 0, 11),
    ("AUD-IA-2026-H1", 2, 34),
    ("AUD-QA-2026-Q2", 0, 9),
    ("AUD-QA-2026-Q2", 1, 21),
    ("AUD-REL-2026-07", 1, 26),
    ("AUD-DOC-2026-09", 1, 19),
    ("AUD-DOC-2026-09", 2, 30),
    ("AUD-IA-2026-H2", 1, 24),
    ("AUD-IA-2026-H2", 2, 17),
    ("AUD-QA-2027-Q1", 1, 15),
    ("AUD-REL-2026-07", 0, 41),
    ("AUD-DOC-2026-09", 0, 38),
]

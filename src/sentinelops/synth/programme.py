"""The audit programme — the other scheduled thing, and the findings it raises.

Section 1 keeps audits and compliance activities apart, and the corpus has to as
well or the distinction is only a paragraph in a document. So the generator
carries a programme: eight audits across the eighteen months, covering all four
kinds the stakeholder named, each raising between two and six findings.

**The descriptions are free text with no category label**, and that is the whole
point of them. Section 1 says plainly that no standard gap taxonomy exists and
that the auditor describes each gap in their own words. So the same underlying
failure is written three different ways here by two different auditors months
apart — "still held privileged access", "retained active accounts and VPN
access", "remained enabled five months after the engagement closed". A corpus
whose descriptions were drawn from a fixed vocabulary would make the
classification model look far better than it is, and would make recurrence
detection trivial rather than the thing section 2 says needs a model.

`RECURRENCE_GROUPS` records which of them are *intended* to be the same gap.
Nothing in the pipeline reads it — it goes into the isolated truth file, so that
recurrence detection can be **scored** rather than admired. Before this, the
detector's output could be eyeballed and called plausible; now it can be wrong.
"""

from __future__ import annotations

from datetime import date

#: (id, kind, planned, conducted, auditor, scope, title)
#:
#: Seven conducted, one still ahead of "today" (15 April 2027) so the upcoming
#: panel has something genuinely upcoming and the programme does not read as
#: though auditing stopped.
AUDIT_PROGRAMME: list[tuple] = [
    ("AUD-IA-2026-H1", "internal_audit", date(2026, 3, 9), date(2026, 3, 20),
     "ID-PA-KAUR",
     ["AREA-IT", "AREA-HR", "AREA-FINANCE"],
     "Internal Audit — H1 2026, core support functions"),
    ("AUD-QA-2026-Q2", "qarev", date(2026, 5, 11), date(2026, 5, 22),
     "ID-PA-OSEI",
     ["AREA-IT", "AREA-PRJ-ATLAS"],
     "QAREV — IT and Project Atlas"),
    ("AUD-REL-2026-07", "release_audit", date(2026, 7, 6), date(2026, 7, 10),
     "ID-PA-KAUR",
     ["AREA-PRJ-ATLAS", "AREA-PRJ-BEACON"],
     "Release Audit — Atlas 2.0 and Beacon pilot"),
    ("AUD-DOC-2026-09", "document_review", date(2026, 9, 7), date(2026, 9, 18),
     "ID-PA-OSEI",
     ["AREA-PURCHASE", "AREA-FINANCE", "AREA-ADMIN"],
     "Controlled document review — purchase, finance and admin"),
    ("AUD-IA-2026-H2", "internal_audit", date(2026, 11, 2), date(2026, 11, 13),
     "ID-PA-KAUR",
     ["AREA-ADMIN", "AREA-FACILITIES", "AREA-PRJ-CORAL"],
     "Internal Audit — H2 2026, admin, facilities and Project Coral"),
    ("AUD-QA-2027-Q1", "qarev", date(2027, 2, 8), date(2027, 2, 19),
     "ID-PA-OSEI",
     ["AREA-HR", "AREA-PRJ-BEACON", "AREA-PRJ-DELTA"],
     "QAREV — HR, Beacon and Delta"),
    ("AUD-REL-2027-03", "release_audit", date(2027, 3, 15), date(2027, 3, 19),
     "ID-PA-KAUR",
     ["AREA-PRJ-CORAL", "AREA-IT"],
     "Release Audit — Coral first release"),
    # Planned, not yet conducted at the vantage point.
    ("AUD-DOC-2027-05", "document_review", date(2027, 5, 4), None,
     "ID-PA-OSEI",
     ["AREA-FACILITIES", "AREA-HR"],
     "Controlled document review — facilities and HR"),
]

#: (audit_id, unit_id, severity, description, agreed action plan)
#:
#: Severities spread across all three deliberately. Between two and six findings
#: per audit, weighted the way real ones are: a first internal audit of a
#: function turns up more than a follow-up release audit.
AUDIT_FINDINGS: list[tuple[str, str, str, str, str]] = [
    # --- AUD-IA-2026-H1 — five findings --------------------------------------
    ("AUD-IA-2026-H1", "AREA-IT", "Major",
     "Three staff who left the infrastructure team in January still held "
     "privileged access to the production console at the time of the audit. The "
     "joiners-movers-leavers checklist was completed but the access revocation "
     "step was not evidenced for any of the three.",
     "Revoke the three accounts, and add a monthly reconciliation between HR "
     "leaver records and privileged access holders."),
    ("AUD-IA-2026-H1", "AREA-IT", "Minor",
     "The risk register for IT was last reviewed in September and three of the "
     "risks rated high carry mitigations whose owners have since left.",
     "Review the register and reassign the orphaned mitigations."),
    ("AUD-IA-2026-H1", "AREA-HR", "Observation",
     "Security awareness training completion is tracked in a spreadsheet that "
     "several people can edit without any record of who changed what. No "
     "discrepancy was found, but the tracker cannot be relied on as evidence.",
     "Move the tracker to the LMS export, or restrict edit rights and enable "
     "version history."),
    ("AUD-IA-2026-H1", "AREA-FINANCE", "Minor",
     "The finance process manual is two versions behind the process actually "
     "followed. The quarterly close steps were changed in March and the manual "
     "still describes the old sequence.",
     "Update the manual and align the review cycle to the process change log."),
    ("AUD-IA-2026-H1", "AREA-FINANCE", "Observation",
     "Findings closed during the last cycle were marked closed by the owning "
     "team rather than validated by the auditor. Nothing was found to be "
     "wrongly closed, but the validation step is not evidenced.",
     "Record the auditor's validation against each closure."),
    # --- AUD-QA-2026-Q2 — three findings -------------------------------------
    ("AUD-QA-2026-Q2", "AREA-IT", "Major",
     "Backup restore verification for the primary datastore has been recorded "
     "as 'passed' each month, but the team could not produce the restore logs "
     "for March or April. The verification appears to have been signed off "
     "without the test being run.",
     "Re-run the restore test for both months and retain the logs with the "
     "sign-off."),
    ("AUD-QA-2026-Q2", "AREA-PRJ-ATLAS", "Minor",
     "Project Atlas has no entry in the risk register despite handling customer "
     "personal data. The project was stood up in February and the register was "
     "last reviewed in January.",
     "Add Atlas to the register and bring forward the next review."),
    ("AUD-QA-2026-Q2", "AREA-PRJ-ATLAS", "Observation",
     "Atlas keeps its own copy of the process documentation rather than "
     "referencing the controlled set, so the two can drift apart unnoticed.",
     "Reference the controlled documents rather than copying them."),
    # --- AUD-REL-2026-07 — two findings --------------------------------------
    ("AUD-REL-2026-07", "AREA-PRJ-ATLAS", "Major",
     "The Atlas 2.0 release went to production without the pre-release security "
     "review being completed. The review was scheduled and then skipped when "
     "the release date moved forward; no exception was raised.",
     "Complete the review retrospectively and make it a release gate that "
     "cannot be skipped without a recorded exception."),
    ("AUD-REL-2026-07", "AREA-PRJ-BEACON", "Observation",
     "Beacon's change log records what was deployed but not who approved it. No "
     "unapproved change was identified.",
     "Record the approver against each change."),
    # --- AUD-DOC-2026-09 — four findings -------------------------------------
    ("AUD-DOC-2026-09", "AREA-PURCHASE", "Major",
     "Due diligence files for two suppliers onboarded in Q2 contain no "
     "financial standing check and no signed information security schedule. "
     "Both suppliers have access to internal systems.",
     "Complete both files, and block supplier activation until due diligence is "
     "signed off."),
    ("AUD-DOC-2026-09", "AREA-ADMIN", "Minor",
     "Four controlled documents are past their review date, the oldest by seven "
     "months. All four are still in active use.",
     "Review all four and set calendar reminders ahead of the review dates."),
    ("AUD-DOC-2026-09", "AREA-FINANCE", "Minor",
     "The controlled document register does not reconcile to the documents "
     "actually in use: two procedures in daily use appear nowhere in it.",
     "Reconcile the register and add the two missing procedures."),
    ("AUD-DOC-2026-09", "AREA-ADMIN", "Observation",
     "Superseded versions of the travel policy remain on the shared drive "
     "alongside the current one, with nothing to distinguish them.",
     "Withdraw superseded versions from the shared drive."),
    # --- AUD-IA-2026-H2 — six findings ---------------------------------------
    ("AUD-IA-2026-H2", "AREA-ADMIN", "Major",
     "Contractors whose engagements ended in August and September retained "
     "active accounts and building access. Four accounts were still enabled at "
     "the time of the audit, one of them used after the engagement end date.",
     "Disable all four immediately and tie account expiry to the contract end "
     "date in the joiners-movers-leavers process."),
    ("AUD-IA-2026-H2", "AREA-FACILITIES", "Major",
     "The contractor management file for the site services provider has no "
     "current insurance certificate and no signed security schedule, and the "
     "provider holds out-of-hours building access.",
     "Obtain both documents or suspend out-of-hours access."),
    ("AUD-IA-2026-H2", "AREA-FACILITIES", "Minor",
     "The facilities risk register has not been reviewed since the site "
     "consolidation began, so it still describes two sites that have closed.",
     "Review the register against the current site list."),
    ("AUD-IA-2026-H2", "AREA-PRJ-CORAL", "Minor",
     "Coral's data protection impact assessment was drafted but never approved. "
     "It has sat in draft since the project started.",
     "Complete and approve the assessment before the first release."),
    ("AUD-IA-2026-H2", "AREA-PRJ-CORAL", "Observation",
     "Coral records its process changes in the team's own wiki, which is not "
     "part of the controlled document set.",
     "Bring the process pages into the controlled set."),
    ("AUD-IA-2026-H2", "AREA-ADMIN", "Observation",
     "Personal data held in the visitor log has no retention period recorded "
     "against it, although the log is cleared informally each year.",
     "Record a retention period and schedule the deletion."),
    # --- AUD-QA-2027-Q1 — four findings --------------------------------------
    ("AUD-QA-2027-Q1", "AREA-HR", "Major",
     "A third-party payroll integration partner's access to the HR system "
     "remained enabled five months after the engagement closed. The access was "
     "not used, but nobody had reviewed it.",
     "Revoke the access and add third-party credentials to the quarterly access "
     "review scope."),
    ("AUD-QA-2027-Q1", "AREA-PRJ-BEACON", "Minor",
     "Beacon's supplier records are incomplete: the security questionnaire is "
     "missing for one of the three suppliers the project uses directly, and "
     "that supplier was activated before the file was opened.",
     "Obtain the questionnaire, or route the supplier through Purchase."),
    ("AUD-QA-2027-Q1", "AREA-PRJ-DELTA", "Minor",
     "Delta went live with two new processes in January that were never "
     "reviewed for compliance impact before deployment.",
     "Review both retrospectively and add the gate to the deployment checklist."),
    ("AUD-QA-2027-Q1", "AREA-HR", "Observation",
     "Prior audit findings for HR are tracked in a spreadsheet separate from "
     "the findings register, so the two counts disagree by three.",
     "Track findings in one place."),
    # --- AUD-REL-2027-03 — three findings ------------------------------------
    ("AUD-REL-2027-03", "AREA-PRJ-CORAL", "Major",
     "The Coral release shipped with a database account whose password had not "
     "been rotated since the project began, and which is shared between two "
     "services.",
     "Rotate the credential, split it per service, and bring both into the key "
     "rotation schedule."),
    ("AUD-REL-2027-03", "AREA-IT", "Minor",
     "Two changes deployed alongside the Coral release were recorded in the "
     "change log after the fact rather than reviewed before go-live.",
     "Review both retrospectively and enforce the pre-deployment gate."),
    ("AUD-REL-2027-03", "AREA-IT", "Observation",
     "Post-incident reviews are completed but the actions arising from them are "
     "tracked in the incident ticket rather than anywhere that survives the "
     "ticket being closed.",
     "Track post-incident actions in the same place as audit findings."),
]

#: What the corpus *intends* to be the same gap, for scoring recurrence.
#:
#: Nothing in the pipeline reads this. It travels into the isolated truth file
#: so `evaluation` can ask the only question that matters about a recurrence
#: detector: of the sets we planted, how many did it find, and how many links
#: did it invent? Without it the detector's output can be admired but not
#: marked, and "it found the recurrence" is a claim about a screenshot.
#:
#: Each group is a list of (audit_id, index-within-that-audit's-findings), which
#: survives a renumbering of finding ids. Two groups, exactly as section 10 asks,
#: and both cross the support-function / project-team line.
RECURRENCE_GROUPS: dict[str, dict] = {
    "REC-AUDIT-ACCESS-LEAVERS": {
        "gap": "Access left active after the person or engagement had gone",
        "members": [
            ("AUD-IA-2026-H1", 0),   # IT — leavers with privileged access
            ("AUD-IA-2026-H2", 0),   # Admin — contractors with active accounts
            ("AUD-QA-2027-Q1", 0),   # HR — payroll partner still enabled
        ],
        "note": (
            "Three units, eleven months apart, written by two auditors with no "
            "shared vocabulary: 'still held privileged access', 'retained "
            "active accounts and building access', 'remained enabled five "
            "months after the engagement closed'."
        ),
    },
    "REC-AUDIT-SUPPLIER-FILES": {
        "gap": "A supplier went live before its due diligence file was complete",
        "members": [
            ("AUD-DOC-2026-09", 0),  # Purchase — two suppliers, no checks
            ("AUD-IA-2026-H2", 1),   # Facilities — site services provider
            ("AUD-QA-2027-Q1", 1),   # Beacon — questionnaire missing
        ],
        "note": (
            "A support function, a second support function and a project team, "
            "spanning seven months. The project team bought directly rather "
            "than through Purchase, which is exactly why nobody joined these up."
        ),
    },
}

#: Which findings an auditor later closed, and how long it took.
#:
#: Left as data rather than derived, because "the auditor was satisfied" is a
#: decision, and a corpus that invents those wholesale describes a system where
#: closure is automatic — the opposite of what section 4 says.
#:
#: (audit_id, index within that audit's findings, days after raising)
AUDIT_CLOSURES: list[tuple[str, int, int]] = [
    ("AUD-IA-2026-H1", 0, 11),
    ("AUD-IA-2026-H1", 2, 34),
    ("AUD-IA-2026-H1", 3, 26),
    ("AUD-IA-2026-H1", 4, 41),
    ("AUD-QA-2026-Q2", 0, 9),
    ("AUD-QA-2026-Q2", 1, 21),
    ("AUD-REL-2026-07", 0, 38),
    ("AUD-REL-2026-07", 1, 26),
    ("AUD-DOC-2026-09", 0, 33),
    ("AUD-DOC-2026-09", 1, 19),
    ("AUD-DOC-2026-09", 2, 30),
    ("AUD-DOC-2026-09", 3, 47),
    ("AUD-IA-2026-H2", 0, 22),
    ("AUD-IA-2026-H2", 3, 24),
    ("AUD-IA-2026-H2", 4, 17),
    ("AUD-IA-2026-H2", 5, 51),
    ("AUD-QA-2027-Q1", 1, 15),
    ("AUD-QA-2027-Q1", 3, 28),
    ("AUD-REL-2027-03", 1, 12),
    ("AUD-REL-2027-03", 2, 18),
    ("AUD-IA-2026-H2", 2, 39),
    ("AUD-QA-2026-Q2", 2, 44),
]

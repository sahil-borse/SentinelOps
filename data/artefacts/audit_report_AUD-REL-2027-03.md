# Release Audit — Coral first release

| | |
|---|---|
| Audit | `AUD-REL-2027-03` |
| Kind | Release Audit |
| Auditor | P. Kaur |
| Scope | Project Coral, IT |
| Planned | 2027-03-15 |
| Conducted | 2027-03-19 |
| Findings | 3 |
| Report | issued 2027-04-15 by P. Kaur, after confirmation by P. Kaur on 2027-04-15 |

## Summary

The audit of the Coral first release identified three findings across Project Coral and IT, with issues spanning credential management, change validation, and record keeping [FND-REL-2027-03-01, FND-REL-2027-03-02, FND-REL-2027-03-03]. Project Coral was found to have shipped with a database account whose password had not been rotated since project inception and was shared between two services, indicating a significant credential management failure [FND-REL-2027-03-01]. Within IT, two changes related to the release were logged after deployment rather than being reviewed beforehand, repeating a previously observed gap in change validation [FND-REL-2027-03-02]. Additionally, IT's post-incident review actions are tracked only within incident tickets, which do not persist after closure, reflecting a recurring issue with inadequate record keeping [FND-REL-2027-03-03].

_Drafted from the findings below (audit_report_v3); every statement cites the findings it rests on. Confirmed by P. Kaur before issue._

## Findings

3 raised — 1 Major, 1 Minor, 1 Observation.

### FND-REL-2027-03-01 — Major

- **Unit** Project Coral
- **Category** credential_management_failure
- **Owner** M. Dubois · **target** 2027-03-26

The Coral release shipped with a database account whose password had not been rotated since the project began, and which is shared between two services.

**Agreed action plan.** Rotate the credential, split it per service, and bring both into the key rotation schedule.

### FND-REL-2027-03-02 — Minor

- **Unit** IT
- **Category** lack_of_required_validation_or_approval
- **Owner** Y. Nakamura · **target** 2027-04-02

Two changes deployed alongside the Coral release were recorded in the change log after the fact rather than reviewed before go-live.

**Agreed action plan.** Review both retrospectively and enforce the pre-deployment gate.

**Recurrence.** Resembles FND-REL-2026-07-01 (Project Atlas, raised 2026-07-10).

### FND-REL-2027-03-03 — Observation

- **Unit** IT
- **Category** unreliable_or_inadequate_record_keeping
- **Owner** Y. Nakamura · **target** 2027-04-16

Post-incident reviews are completed but the actions arising from them are tracked in the incident ticket rather than anywhere that survives the ticket being closed.

**Agreed action plan.** Track post-incident actions in the same place as audit findings.

**Recurrence.** Resembles FND-INCIDENT-PM-IT-2026-02 (IT, raised 2026-03-28); FND-INCIDENT-PM-IT-2026-03 (IT, raised 2026-04-28); FND-INCIDENT-PM-IT-2026-04 (IT, raised 2026-05-28).


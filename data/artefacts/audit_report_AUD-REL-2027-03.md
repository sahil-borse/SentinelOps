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

This audit raised 3 finding(s) across 2 auditable unit(s) [FND-REL-2027-03-01, FND-REL-2027-03-02, FND-REL-2027-03-03]. The weight of the audit sits in 1 Major finding(s) [FND-REL-2027-03-01], which carry the shortest target dates. IT accounts for 2 of them [FND-REL-2027-03-02, FND-REL-2027-03-03]. The same gap category, change_not_authorised, appears more than once [FND-REL-2027-03-01, FND-REL-2027-03-02], which is the pattern worth attention here.

_Drafted from the findings below (audit_report_v2); every statement cites the findings it rests on. Confirmed by P. Kaur before issue._

## Findings

3 raised — 1 Major, 1 Minor, 1 Observation.

### FND-REL-2027-03-01 — Major

- **Unit** Project Coral
- **Category** change_not_authorised
- **Owner** M. Dubois · **target** 2027-03-26

The Coral release shipped with a database account whose password had not been rotated since the project began, and which is shared between two services.

**Agreed action plan.** Rotate the credential, split it per service, and bring both into the key rotation schedule.

### FND-REL-2027-03-02 — Minor

- **Unit** IT
- **Category** change_not_authorised
- **Owner** Y. Nakamura · **target** 2027-04-02

Two changes deployed alongside the Coral release were recorded in the change log after the fact rather than reviewed before go-live.

**Agreed action plan.** Review both retrospectively and enforce the pre-deployment gate.

### FND-REL-2027-03-03 — Observation

- **Unit** IT
- **Category** incident_follow_up_incomplete
- **Owner** Y. Nakamura · **target** 2027-04-16

Post-incident reviews are completed but the actions arising from them are tracked in the incident ticket rather than anywhere that survives the ticket being closed.

**Agreed action plan.** Track post-incident actions in the same place as audit findings.


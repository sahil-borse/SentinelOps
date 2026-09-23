# Prioritisation brief — 2027-04-15

Advisory; changes no state. 1 model call over the top 12 of 84 open findings, 41 section 8 metrics and 13 counts over the listed rows (brief_v4).

## Top priorities

1. **FND-INCIDENT-PM-IT-2026-01** — IT, Major, 408d past target, chronic (210 points)
   Critical IT post-mortem is 408 days overdue, has 5 recurrence links, and has required 16 chases; this is the oldest and most persistent open issue.

2. **FND-INCIDENT-PM-IT-2026-09** — IT, Major, 166d past target (201 points)
   Critical IT post-mortem is 166 days overdue with 5 recurrence links and 7 chases, indicating repeated failures to address record-keeping.

3. **FND-INCIDENT-PM-PRJ-ATLAS-2026-04** — Project Atlas, Major, 319d past target (200 points)
   Critical Project Atlas post-mortem is 319 days overdue, with 2 recurrence links and 12 chases, showing persistent validation gaps.

4. **FND-INCIDENT-PM-IT-2026-05** — IT, Major, 288d past target (190 points)
   Critical IT post-mortem is 288 days overdue, has 1 recurrence link, and has been chased 13 times, highlighting ongoing record-keeping issues.

5. **FND-CHANGED-PROCESS-IT-2026-10** — IT, Major, 135d past target (175 points)
   Critical IT process review is 135 days overdue, with 1 recurrence link and 5 chases, risking unvalidated process changes.

## Emerging patterns

- IT unit accounts for 8 of the 12 highest-priority major findings, indicating a concentration of overdue and recurring issues in this area.
  _cites: FND-INCIDENT-PM-IT-2026-01; FND-INCIDENT-PM-IT-2026-09; FND-INCIDENT-PM-IT-2026-05; FND-CHANGED-PROCESS-IT-2026-10; FND-INCIDENT-PM-IT-2026-12; FND-BACKUP-VERIFY-IT-2027-02; FND-CHANGED-PROCESS-IT-2027-03; FND-CONTROLLED-DOCS-IT-2027-Q1; listed_in_unit:IT = 8_
- Lack of required validation or approval is the most common category among top findings, appearing in 6 of 12 cases.
  _cites: FND-INCIDENT-PM-IT-2026-01; FND-INCIDENT-PM-PRJ-ATLAS-2026-04; FND-CHANGED-PROCESS-IT-2026-10; FND-INCIDENT-PM-IT-2026-12; FND-BACKUP-VERIFY-IT-2027-02; FND-CHANGED-PROCESS-IT-2027-03; listed_category:lack_of_required_validation_or_approval = 6_
- 9 of the 12 listed major findings are past their target dates, showing a persistent challenge in timely closure.
  _cites: FND-INCIDENT-PM-IT-2026-01; FND-INCIDENT-PM-IT-2026-09; FND-INCIDENT-PM-PRJ-ATLAS-2026-04; FND-INCIDENT-PM-IT-2026-05; FND-CHANGED-PROCESS-IT-2026-10; FND-INCIDENT-PM-IT-2026-12; FND-IA-2026-H2-02; FND-QA-2027-Q1-01; FND-BACKUP-VERIFY-IT-2027-02; listed_past_target = 9_

## Recommended focus

- Prioritize overdue and recurring IT findings, as IT holds 8 of 12 major issues and most are past target dates.
  _cites: FND-INCIDENT-PM-IT-2026-01; FND-INCIDENT-PM-IT-2026-09; FND-INCIDENT-PM-IT-2026-05; FND-CHANGED-PROCESS-IT-2026-10; FND-INCIDENT-PM-IT-2026-12; FND-BACKUP-VERIFY-IT-2027-02; FND-CHANGED-PROCESS-IT-2027-03; FND-CONTROLLED-DOCS-IT-2027-Q1; listed_in_unit:IT = 8; listed_past_target = 9_
- Address systemic gaps in validation and approval processes, as this category appears in half of the top findings.
  _cites: FND-INCIDENT-PM-IT-2026-01; FND-INCIDENT-PM-PRJ-ATLAS-2026-04; FND-CHANGED-PROCESS-IT-2026-10; FND-INCIDENT-PM-IT-2026-12; FND-BACKUP-VERIFY-IT-2027-02; FND-CHANGED-PROCESS-IT-2027-03; listed_category:lack_of_required_validation_or_approval = 6_
- Focus on closing findings with multiple recurrence links, as 9 of 12 listed findings have recurrence, indicating repeated compliance failures.
  _cites: FND-INCIDENT-PM-IT-2026-01; FND-INCIDENT-PM-IT-2026-09; FND-INCIDENT-PM-PRJ-ATLAS-2026-04; FND-INCIDENT-PM-IT-2026-05; FND-CHANGED-PROCESS-IT-2026-10; FND-INCIDENT-PM-IT-2026-12; FND-QA-2027-Q1-01; FND-CHANGED-PROCESS-IT-2027-03; FND-CONTROLLED-DOCS-IT-2027-Q1; listed_with_recurrence_links = 9_

## The ranking

| rank | finding | unit | band | timing | points |
|---:|---|---|---|---|---:|
| 1 | FND-INCIDENT-PM-IT-2026-01 | IT | Major | 408d past target, chronic | 210 |
| 2 | FND-INCIDENT-PM-IT-2026-09 | IT | Major | 166d past target | 201 |
| 3 | FND-INCIDENT-PM-PRJ-ATLAS-2026-04 | Project Atlas | Major | 319d past target | 200 |
| 4 | FND-INCIDENT-PM-IT-2026-05 | IT | Major | 288d past target | 190 |
| 5 | FND-CHANGED-PROCESS-IT-2026-10 | IT | Major | 135d past target | 175 |
| 6 | FND-INCIDENT-PM-IT-2026-12 | IT | Major | 74d past target | 156 |
| 7 | FND-IA-2026-H2-02 | Facilities | Major | 146d past target | 138 |
| 8 | FND-QA-2027-Q1-01 | HR | Major | 48d past target | 127 |
| 9 | FND-BACKUP-VERIFY-IT-2027-02 | IT | Major | 15d past target | 78 |
| 10 | FND-CHANGED-PROCESS-IT-2027-03 | IT | Major | 3d to target | 67 |

## How the order is built

```text
Findings are ordered by severity band (Major, then Minor, then Observation), and within a band by points = criticality + timing + recurrence + follow-ups.

  bands         Major > Minor > Observation; nothing lifts a finding past a higher band, however old
  criticality   critical 30 / high 20 / medium 10 / low 0
  timing        30 on the target date; +1 a day past it, up to 90 days; -1 a day before it, 0 from 30 days out
  recurrence    +10 per link to an earlier or later finding, up to 3 links
  follow-ups    +3 per reminder or insufficient round, up to 10

  points within a band run 0 to 210; ties go to the earlier target date, then the id
  chronic       more than 365 days past target: flagged separately for PA/InfoSec; does not change the order
```

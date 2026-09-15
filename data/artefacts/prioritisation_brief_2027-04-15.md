# Prioritisation brief — 2027-04-15

Advisory; changes no state. 1 model call over the top 12 of 20 open findings, 44 section 8 metrics and 16 counts over the listed rows (brief_v3).

## Top priorities

1. **FND-CHANGED-PROCESS-IT-2026-10** — IT, Major, 135d past target (195 points)
   Major in IT (critical unit), 135d past target, chased 5x

2. **FND-IA-2026-H1-02** — IT, Major (raised Minor), 377d past target (190 points)
   Minor in IT (critical unit), 377d past target, chased 13x

3. **FND-IA-2026-H2-02** — Facilities, Major, 146d past target (138 points)
   Major in Facilities (low unit), 146d past target, chased 6x

## Emerging patterns

- IT holds 6 of the most urgent findings.
  _cites: FND-CHANGED-PROCESS-IT-2026-10; FND-IA-2026-H1-02; FND-BACKUP-VERIFY-IT-2027-02; FND-CHANGED-PROCESS-IT-2027-03; FND-CONTROLLED-DOCS-IT-2027-Q1; listed_in_unit:IT = 6_
- The access not revoked category appears 4 times among them.
  _cites: FND-IA-2026-H2-02; FND-QA-2027-Q1-01; FND-FINDING-CLOSURE-IT-2027-Q1; FND-FINDING-CLOSURE-HR-2026-Q2; listed_category:access_not_revoked = 4_

## Recommended focus

- Start with the top of the ranking, in IT.
  _cites: FND-CHANGED-PROCESS-IT-2026-10; overdue_90_plus = 6; oldest_overdue_days = 377_
- Open findings are rising across the window, so new intake deserves as much attention as the backlog.
  _cites: trend_direction = rising; trend_recent_direction = flat_

## The ranking

| rank | finding | unit | band | timing | points |
|---:|---|---|---|---|---:|
| 1 | FND-CHANGED-PROCESS-IT-2026-10 | IT | Major | 135d past target | 195 |
| 2 | FND-IA-2026-H1-02 | IT | Major (raised Minor) | 377d past target | 190 |
| 3 | FND-IA-2026-H2-02 | Facilities | Major | 146d past target | 138 |
| 4 | FND-QA-2027-Q1-01 | HR | Major | 48d past target | 117 |
| 5 | FND-BACKUP-VERIFY-IT-2027-02 | IT | Major | 15d past target | 98 |
| 6 | FND-CHANGED-PROCESS-IT-2027-03 | IT | Major | 3d to target | 87 |
| 7 | FND-CONTROLLED-DOCS-IT-2027-Q1 | IT | Major | 3d to target | 87 |
| 8 | FND-CONTROLLED-DOCS-PRJ-ATLAS-2027-Q1 | Project Atlas | Major | 3d to target | 87 |
| 9 | FND-FINDING-CLOSURE-IT-2027-Q1 | IT | Major | 3d to target | 87 |
| 10 | FND-REL-2027-03-01 | Project Coral | Major | 20d past target | 56 |

## How the order is built

```text
Findings are ordered by severity band (Major, then Minor, then Observation; a finding more than 365 days past its target counts one band higher), and within a band by points = criticality + timing + recurrence + follow-ups.

  bands         Major > Minor > Observation; points never lift a finding past a higher band
  aged up       more than 365 days past target (a full annual audit cycle): one band higher, never more, never above Major
  criticality   critical 30 / high 20 / medium 10 / low 0
  timing        30 on the target date; +1 a day past it, up to 90 days; -1 a day before it, 0 from 30 days out
  recurrence    +10 per link to an earlier or later finding, up to 3 links
  follow-ups    +3 per reminder or insufficient round, up to 10

  points within a band run 0 to 210; ties go to the earlier target date, then the id
```

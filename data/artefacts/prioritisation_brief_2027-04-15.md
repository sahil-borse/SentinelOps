# Prioritisation brief — 2027-04-15

Advisory; changes no state. 1 model call over the top 12 of 20 open findings and 44 named section 8 metrics (brief_v2).

## Top priorities

1. **FND-CHANGED-PROCESS-IT-2026-10** — IT, Major, 135d past target (score 225)
   Major in IT (critical unit), 135d past target, chased 5x

2. **FND-FINDING-CLOSURE-HR-2026-Q2** — HR, Minor, 247d past target (score 202)
   Minor in HR (high unit), 247d past target, chased 9x

3. **FND-IA-2026-H1-02** — IT, Minor, 377d past target (score 190)
   Minor in IT (critical unit), 377d past target, chased 13x

## Emerging patterns

- IT holds 6 of the most urgent findings.
  _cites: FND-CHANGED-PROCESS-IT-2026-10; FND-IA-2026-H1-02; FND-BACKUP-VERIFY-IT-2027-02; FND-CHANGED-PROCESS-IT-2027-03; FND-CONTROLLED-DOCS-IT-2027-Q1; open_in_unit:IT = 6_
- The access not revoked category appears 4 times among them.
  _cites: FND-FINDING-CLOSURE-HR-2026-Q2; FND-IA-2026-H2-02; FND-QA-2027-Q1-01; FND-FINDING-CLOSURE-IT-2027-Q1; recurring_category:access_not_revoked = 24_

## Recommended focus

- Start with the top of the ranking, in IT.
  _cites: FND-CHANGED-PROCESS-IT-2026-10; overdue_90_plus = 6; oldest_overdue_days = 377_
- Open findings are rising across the window, so new intake deserves as much attention as the backlog.
  _cites: trend_direction = rising; trend_recent_direction = flat_

## The ranking

| rank | finding | unit | severity | timing | score |
|---:|---|---|---|---|---:|
| 1 | FND-CHANGED-PROCESS-IT-2026-10 | IT | Major | 135d past target | 225 |
| 2 | FND-FINDING-CLOSURE-HR-2026-Q2 | HR | Minor | 247d past target | 202 |
| 3 | FND-IA-2026-H1-02 | IT | Minor | 377d past target | 190 |
| 4 | FND-CHANGED-PROCESS-FACILITIES-2026-07 | Facilities | Observation | 202d past target | 181.5 |
| 5 | FND-IA-2026-H2-02 | Facilities | Major | 146d past target | 168 |
| 6 | FND-DATA-RETENTION-HR-2026-Q3 | HR | Minor | 155d past target | 163 |
| 7 | FND-QA-2027-Q1-01 | HR | Major | 48d past target | 147 |
| 8 | FND-BACKUP-VERIFY-IT-2027-02 | IT | Major | 15d past target | 128 |
| 9 | FND-CHANGED-PROCESS-IT-2027-03 | IT | Major | 3d to target | 117 |
| 10 | FND-CONTROLLED-DOCS-IT-2027-Q1 | IT | Major | 3d to target | 117 |

## How the score is built

```text
priority score = severity x criticality + timing + recurrence + follow-ups

  severity      Major 40 / Minor 20 / Observation 10
  criticality   critical x1.5 / high x1.25 / medium x1 / low x0.75
  timing        30 on the target date; +1 a day past it, up to 90 days; -1 a day before it, 0 from 30 days out
  recurrence    +10 per link to an earlier or later finding, up to 3 links
  follow-ups    +3 per reminder or insufficient round, up to 10

  range 7.5 to 240; ties go to the earlier target date, then the id
```

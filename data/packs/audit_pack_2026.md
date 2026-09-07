# Audit Evidence Pack — Northwind Group (fictional)

**Period covered** 2026-01-01 to 2026-12-31  
**Scope** All process areas, all applicable controls  
**Generated** 2026-09-02 03:47:30  
**Source** append-only audit log, 725 events  
**Chain integrity** VERIFIED — 725 entries, chain intact

| | |
|---|---|
| Process areas | 7 |
| Controls exercised | 14 |
| Checks due | 143 |
| Checks completed | 84 |
| Checks waived | 0 |
| Checks not examined | 59 |
| Findings recorded | 85 |
| Findings superseded by re-assessment | 1 |
| Current non-compliant findings | 44 |
| Flagged for human review | 0 |
| Decided without a model call | 43 |
| Exceptions on register | 4 |
| Actions raised | 45 |
| Actions resolved | 1 |

## 1. Coverage

| Area | Control | Frequency | Due | Completed | Waived | Not examined |
|---|---|---|---|---|---|---|
| Customer Operations | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| Customer Operations | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| Customer Operations | Backup restore verification | monthly | 4 | 3 | 0 | 1 |
| Customer Operations | Business continuity plan test | annual | 1 | 0 | 0 | 1 |
| Customer Operations | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Customer Operations | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| Customer Operations | Customer complaint handling SLA | monthly | 4 | 3 | 0 | 1 |
| Customer Operations | Data retention schedule adherence | quarterly | 2 | 1 | 0 | 1 |
| Customer Operations | Data protection impact assessment currency | annual | 1 | 0 | 0 | 1 |
| Customer Operations | Incident post-mortem completion | monthly | 4 | 3 | 0 | 1 |
| Customer Operations | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Financial Reporting | Backup restore verification | monthly | 4 | 3 | 0 | 1 |
| Financial Reporting | Business continuity plan test | annual | 1 | 0 | 0 | 1 |
| Financial Reporting | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Financial Reporting | Incident post-mortem completion | monthly | 4 | 3 | 0 | 1 |
| Financial Reporting | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Change management approval | monthly | 4 | 3 | 0 | 1 |
| People Operations | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Data retention schedule adherence | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Data protection impact assessment currency | annual | 1 | 0 | 0 | 1 |
| People Operations | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| People Operations | Third-party access recertification | quarterly | 2 | 2 | 0 | 0 |
| People Operations | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
| Marketing | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| Marketing | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| Marketing | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Marketing | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| Marketing | Customer complaint handling SLA | monthly | 4 | 3 | 0 | 1 |
| Marketing | Data retention schedule adherence | quarterly | 2 | 1 | 0 | 1 |
| Marketing | Data protection impact assessment currency | annual | 1 | 1 | 0 | 0 |
| Marketing | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| Marketing | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Marketing | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
| Payments Processing | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| Payments Processing | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| Payments Processing | Backup restore verification | monthly | 4 | 3 | 0 | 1 |
| Payments Processing | Business continuity plan test | annual | 1 | 0 | 0 | 1 |
| Payments Processing | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Payments Processing | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| Payments Processing | Customer complaint handling SLA | monthly | 4 | 3 | 0 | 1 |
| Payments Processing | Data retention schedule adherence | quarterly | 2 | 1 | 0 | 1 |
| Payments Processing | Data protection impact assessment currency | annual | 1 | 0 | 0 | 1 |
| Payments Processing | Incident post-mortem completion | monthly | 4 | 3 | 0 | 1 |
| Payments Processing | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| Payments Processing | Third-party access recertification | quarterly | 2 | 1 | 0 | 1 |
| Payments Processing | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Payments Processing | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
| Platform Engineering | Backup restore verification | monthly | 4 | 3 | 0 | 1 |
| Platform Engineering | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Platform Engineering | Incident post-mortem completion | monthly | 4 | 3 | 0 | 1 |
| Platform Engineering | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| Platform Engineering | Third-party access recertification | quarterly | 2 | 1 | 0 | 1 |
| Platform Engineering | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Platform Engineering | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
| Procurement | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Procurement | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| Procurement | Third-party access recertification | quarterly | 2 | 2 | 0 | 0 |
| Procurement | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Procurement | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |

## 2. Exception register

| Reference | Control | Area | Approved by | Granted | Expires | Status |
|---|---|---|---|---|---|---|
| EXC-001 | CTRL-BCP-TEST | AREA-PLATFORM | Group Risk Committee | 2026-01-15 | 2026-12-31 | active |
| EXC-002 | CTRL-THIRD-PARTY-ACCESS | AREA-MKTG | Chief Procurement Officer | 2026-01-01 | 2026-06-30 | active |
| EXC-003 | CTRL-INCIDENT-PM | AREA-FINREP | Finance Control Board | 2026-02-01 | 2026-12-31 | revoked |
| EXC-004 | CTRL-CRYPTO-KEY | AREA-HR | Chief Information Security Officer | 2026-05-11 | 2026-06-19 | active |

**EXC-001** — Continuity exercise deferred while the disaster recovery estate is migrated to the new region. Migration completes Q1 2027.

**EXC-002** — Third-party access recertification waived for the agency roster pending consolidation of marketing suppliers under a single master agreement. Consolidation was due to complete by 30 June.

**EXC-003** — Post-mortem requirement waived during the reporting platform freeze. Withdrawn after the audit committee objected.

**EXC-004** — Q1 key rotation for the HR data store was not carried out before the payroll platform migration froze the key management service. Rotation is deferred and the outstanding Q1 obligation waived, on the compensating control of a manual key inventory signed off by the platform team. Expires at migration cutover.

## 3. Findings register

### FND-ACCESS-EXPORT-CUSTOPS-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### FND-ACCESS-EXPORT-HR-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-HR-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### FND-ACCESS-EXPORT-MKTG-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-MKTG-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### FND-ACCESS-EXPORT-PAYMENTS-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Threshold evaluation failed: dormant_unresolved was 45 against a required at most 0; reviewed_pct was 82.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 45
- **Cited evidence** > "reviewed_pct": 82.0
- **Gap** dormant_unresolved was 45, outside the required at most 0.
- **Gap** reviewed_pct was 82.0, outside the required at least 100.0.

### FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 *(superseded by FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-2)*

- **Check** CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. The report records neither a reviewer name nor a review date.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `431030406cc7`

### FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-2

- **Check** CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - AREA-CUSTOPS - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `810ca9d99429`

### FND-ACCESS-REVIEW-HR-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-HR-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 3. 4 dormant accounts were identified but revocation is still pending and no justification has been recorded for them.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `8ff87a54bac4`

### FND-ACCESS-REVIEW-MKTG-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-MKTG-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 3. 4 dormant accounts were identified but revocation is still pending and no justification has been recorded for them.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `cfd8ac19fa38`

### FND-ACCESS-REVIEW-PAYMENTS-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** No evidence was submitted for 2026-Q1 against Quarterly privileged access review. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### FND-BACKUP-VERIFY-CUSTOPS-2026-01-1

- **Check** CHK-BACKUP-VERIFY-CUSTOPS-2026-01  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** No evidence was submitted for 2026-01 against Backup restore verification. The check fell due on 2026-02-15.
- **Gap** No evidence on file for 2026-01.

### FND-BACKUP-VERIFY-CUSTOPS-2026-02-1

- **Check** CHK-BACKUP-VERIFY-CUSTOPS-2026-02  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** Threshold evaluation failed: max_rto_minutes was 105 against a required at most 60; success_pct was 77.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 105
- **Cited evidence** > "success_pct": 77.0
- **Gap** max_rto_minutes was 105, outside the required at most 60.
- **Gap** success_pct was 77.0, outside the required at least 95.0.

### FND-BACKUP-VERIFY-CUSTOPS-2026-03-1

- **Check** CHK-BACKUP-VERIFY-CUSTOPS-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** All thresholds met: max_rto_minutes was 36 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 36
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-FINREP-2026-01-1

- **Check** CHK-BACKUP-VERIFY-FINREP-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by A. Novak
- **Rationale** All thresholds met: max_rto_minutes was 38 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 38
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-FINREP-2026-02-1

- **Check** CHK-BACKUP-VERIFY-FINREP-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** All thresholds met: max_rto_minutes was 51 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 51
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-FINREP-2026-03-1

- **Check** CHK-BACKUP-VERIFY-FINREP-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** All thresholds met: max_rto_minutes was 51 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 51
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-PAYMENTS-2026-01-1

- **Check** CHK-BACKUP-VERIFY-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** All thresholds met: max_rto_minutes was 28 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 28
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-PAYMENTS-2026-02-1

- **Check** CHK-BACKUP-VERIFY-PAYMENTS-2026-02  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** No evidence was submitted for 2026-02 against Backup restore verification. The check fell due on 2026-03-15.
- **Gap** No evidence on file for 2026-02.

### FND-BACKUP-VERIFY-PAYMENTS-2026-03-1

- **Check** CHK-BACKUP-VERIFY-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** All thresholds met: max_rto_minutes was 33 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 33
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-PLATFORM-2026-01-1

- **Check** CHK-BACKUP-VERIFY-PLATFORM-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by N. Iyer
- **Rationale** All thresholds met: max_rto_minutes was 55 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 55
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-PLATFORM-2026-02-1

- **Check** CHK-BACKUP-VERIFY-PLATFORM-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** All thresholds met: max_rto_minutes was 48 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 48
- **Cited evidence** > "success_pct": 100.0

### FND-BACKUP-VERIFY-PLATFORM-2026-03-1

- **Check** CHK-BACKUP-VERIFY-PLATFORM-2026-03  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** Threshold evaluation failed: max_rto_minutes was 27 against a required at most 60; success_pct was 93.6 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 27
- **Cited evidence** > "success_pct": 93.6
- **Gap** success_pct was 93.6, outside the required at least 95.0.

### FND-CHANGE-MGMT-CUSTOPS-2026-01-1

- **Check** CHK-CHANGE-MGMT-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Customer Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `6ee181d8e7d1`

### FND-CHANGE-MGMT-CUSTOPS-2026-02-1

- **Check** CHK-CHANGE-MGMT-CUSTOPS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Customer Operations - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `7723450ea8e2`

### FND-CHANGE-MGMT-CUSTOPS-2026-03-1

- **Check** CHK-CHANGE-MGMT-CUSTOPS-2026-03  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `wrong_evidence_type`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** The submission is a backup_verification_log, but Change management approval requires change_approval_register. The criteria cannot be assessed against it.
- **Gap** Wrong evidence type: backup_verification_log.

### FND-CHANGE-MGMT-FINREP-2026-01-1

- **Check** CHK-CHANGE-MGMT-FINREP-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Financial Reporting - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `b088627571da`

### FND-CHANGE-MGMT-FINREP-2026-02-1

- **Check** CHK-CHANGE-MGMT-FINREP-2026-02  
- **Verdict** `partial` · confidence 0.62 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** A criterion is only partially evidenced.
- **Cited evidence** > 2. 4 emergency changes occurred; review is complete for 28 of them.
- **Gap** A clause is addressed but not completed.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `203a91b7a583`

### FND-CHANGE-MGMT-FINREP-2026-03-1

- **Check** CHK-CHANGE-MGMT-FINREP-2026-03  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `wrong_evidence_type`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** The submission is a backup_verification_log, but Change management approval requires change_approval_register. The criteria cannot be assessed against it.
- **Gap** Wrong evidence type: backup_verification_log.

### FND-CHANGE-MGMT-HR-2026-01-1

- **Check** CHK-CHANGE-MGMT-HR-2026-01  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by D. Ferreira
- **Rationale** No evidence was submitted for 2026-01 against Change management approval. The check fell due on 2026-02-15.
- **Gap** No evidence on file for 2026-01.

### FND-CHANGE-MGMT-HR-2026-02-1

- **Check** CHK-CHANGE-MGMT-HR-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - People Operations - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `1545a5cc8c37`

### FND-CHANGE-MGMT-HR-2026-03-1

- **Check** CHK-CHANGE-MGMT-HR-2026-03  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. 2 emergency changes were never reviewed.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `3781c63fb336`

### FND-CHANGE-MGMT-MKTG-2026-01-1

- **Check** CHK-CHANGE-MGMT-MKTG-2026-01  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by J. Alvarez
- **Rationale** No evidence was submitted for 2026-01 against Change management approval. The check fell due on 2026-02-15.
- **Gap** No evidence on file for 2026-01.

### FND-CHANGE-MGMT-MKTG-2026-02-1

- **Check** CHK-CHANGE-MGMT-MKTG-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Marketing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `2a258341233c`

### FND-CHANGE-MGMT-MKTG-2026-03-1

- **Check** CHK-CHANGE-MGMT-MKTG-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Marketing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `db7af5002a05`

### FND-CHANGE-MGMT-PAYMENTS-2026-01-1

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Payments Processing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `1b53db8fa216`

### FND-CHANGE-MGMT-PAYMENTS-2026-02-1

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-02  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. 2 emergency changes were never reviewed.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `9176034caebf`

### FND-CHANGE-MGMT-PAYMENTS-2026-03-1

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-03  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** No evidence was submitted for 2026-03 against Change management approval. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-03.

### FND-CHANGE-MGMT-PLATFORM-2026-01-1

- **Check** CHK-CHANGE-MGMT-PLATFORM-2026-01  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by N. Iyer
- **Rationale** No evidence was submitted for 2026-01 against Change management approval. The check fell due on 2026-02-15.
- **Gap** No evidence on file for 2026-01.

### FND-CHANGE-MGMT-PLATFORM-2026-02-1

- **Check** CHK-CHANGE-MGMT-PLATFORM-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Platform Engineering - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `492689ffdc19`

### FND-CHANGE-MGMT-PLATFORM-2026-03-1

- **Check** CHK-CHANGE-MGMT-PLATFORM-2026-03  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 3. No reconciliation against the deployment log was performed.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `1c4c92380b17`

### FND-CHANGE-MGMT-PROC-2026-01-1

- **Check** CHK-CHANGE-MGMT-PROC-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Procurement - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `bdd8803927cc`

### FND-CHANGE-MGMT-PROC-2026-02-1

- **Check** CHK-CHANGE-MGMT-PROC-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Procurement - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `b3a59e5685c8`

### FND-CHANGE-MGMT-PROC-2026-03-1

- **Check** CHK-CHANGE-MGMT-PROC-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Procurement - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `9c8f9db23989`

### FND-CRYPTO-KEY-CUSTOPS-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - Customer Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `efbfea2d3ddc`

### FND-CRYPTO-KEY-HR-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-HR-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** No evidence was submitted for 2026-Q1 against Encryption key rotation. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### FND-CRYPTO-KEY-MKTG-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-MKTG-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `wrong_evidence_type`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** The submission is a access_review_export, but Encryption key rotation requires key_rotation_record. The criteria cannot be assessed against it.
- **Gap** Wrong evidence type: access_review_export.

### FND-CRYPTO-KEY-PAYMENTS-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-PAYMENTS-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by L. Okafor
- **Rationale** Evidence is dated 2025-08-24, 219 days before 2026-Q1 closed, exceeding the 100 day freshness window for Encryption key rotation.
- **Gap** Evidence is 219 days old against a 100 day limit.

### FND-CUST-COMPLAINTS-CUSTOPS-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Customer Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `7c29ffa8ecfc`

### FND-CUST-COMPLAINTS-CUSTOPS-2026-02-1

- **Check** CHK-CUST-COMPLAINTS-CUSTOPS-2026-02  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** No evidence was submitted for 2026-02 against Customer complaint handling SLA. The check fell due on 2026-03-15.
- **Gap** No evidence on file for 2026-02.

### FND-CUST-COMPLAINTS-CUSTOPS-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-CUSTOPS-2026-03  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `wrong_evidence_type`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** The submission is a change_approval_register, but Customer complaint handling SLA requires complaint_sla_report. The criteria cannot be assessed against it.
- **Gap** Wrong evidence type: change_approval_register.

### FND-CUST-COMPLAINTS-MKTG-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-MKTG-2026-01  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by J. Alvarez
- **Rationale** Evidence is dated 2025-10-18, 105 days before 2026-01 closed, exceeding the 45 day freshness window for Customer complaint handling SLA.
- **Gap** Evidence is 105 days old against a 45 day limit.

### FND-CUST-COMPLAINTS-MKTG-2026-02-1

- **Check** CHK-CUST-COMPLAINTS-MKTG-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Marketing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `b979b5c63bc3`

### FND-CUST-COMPLAINTS-MKTG-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-MKTG-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Marketing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `5d3991f11d8c`

### FND-CUST-COMPLAINTS-PAYMENTS-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Payments Processing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `1a0521992604`

### FND-CUST-COMPLAINTS-PAYMENTS-2026-02-1

- **Check** CHK-CUST-COMPLAINTS-PAYMENTS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Payments Processing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `08a5015258c5`

### FND-CUST-COMPLAINTS-PAYMENTS-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Payments Processing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `d31edd7f4a12`

### FND-DATA-RETENTION-CUSTOPS-2026-Q1-1

- **Check** CHK-DATA-RETENTION-CUSTOPS-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by R. Mehta
- **Rationale** Evidence is dated 2025-08-24, 219 days before 2026-Q1 closed, exceeding the 100 day freshness window for Data retention schedule adherence.
- **Gap** Evidence is 219 days old against a 100 day limit.

### FND-DATA-RETENTION-HR-2026-Q1-1

- **Check** CHK-DATA-RETENTION-HR-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 3. The retention schedule has not been confirmed as current.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `05f6e5cdfc83`

### FND-DATA-RETENTION-MKTG-2026-Q1-1

- **Check** CHK-DATA-RETENTION-MKTG-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 1. No retention sweep was run in this period.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `af89dbd8c7ec`

### FND-DATA-RETENTION-PAYMENTS-2026-Q1-1

- **Check** CHK-DATA-RETENTION-PAYMENTS-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** No evidence was submitted for 2026-Q1 against Data retention schedule adherence. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### FND-DPIA-MKTG-2026-1

- **Check** CHK-DPIA-MKTG-2026  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by J. Alvarez
- **Rationale** Evidence is dated 2024-10-28, 794 days before 2026 closed, exceeding the 400 day freshness window for Data protection impact assessment currency.
- **Gap** Evidence is 794 days old against a 400 day limit.

### FND-INCIDENT-PM-CUSTOPS-2026-01-1

- **Check** CHK-INCIDENT-PM-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Customer Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `4e34b8bbe37c`

### FND-INCIDENT-PM-CUSTOPS-2026-02-1

- **Check** CHK-INCIDENT-PM-CUSTOPS-2026-02  
- **Verdict** `partial` · confidence 0.62 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** A criterion is only partially evidenced.
- **Cited evidence** > 3. 23 of 5 carried-in corrective actions were closed; the rest remain open past their due date.
- **Gap** A clause is addressed but not completed.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `b2155bcb92f3`

### FND-INCIDENT-PM-CUSTOPS-2026-03-1

- **Check** CHK-INCIDENT-PM-CUSTOPS-2026-03  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. Contributing factors are recorded but 5 corrective actions have no named owner.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `cb5261bb415a`

### FND-INCIDENT-PM-FINREP-2026-01-1

- **Check** CHK-INCIDENT-PM-FINREP-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Financial Reporting - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `1382b0a64f7a`

### FND-INCIDENT-PM-FINREP-2026-02-1

- **Check** CHK-INCIDENT-PM-FINREP-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Financial Reporting - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `8b7d34e14c29`

### FND-INCIDENT-PM-FINREP-2026-03-1

- **Check** CHK-INCIDENT-PM-FINREP-2026-03  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. Post-mortems record a timeline only, with no contributing factors and no corrective actions.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `14f0bba2c630`

### FND-INCIDENT-PM-PAYMENTS-2026-01-1

- **Check** CHK-INCIDENT-PM-PAYMENTS-2026-01  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. Post-mortems record a timeline only, with no contributing factors and no corrective actions.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `70592af16a58`

### FND-INCIDENT-PM-PAYMENTS-2026-02-1

- **Check** CHK-INCIDENT-PM-PAYMENTS-2026-02  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 1. No post-mortems were filed for the 40 severity 1 and 2 incidents this month.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `f5e2f68a59a4`

### FND-INCIDENT-PM-PAYMENTS-2026-03-1

- **Check** CHK-INCIDENT-PM-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Payments Processing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `1bb651d72587`

### FND-INCIDENT-PM-PLATFORM-2026-01-1

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-01  
- **Verdict** `partial` · confidence 0.62 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by N. Iyer
- **Rationale** A criterion is only partially evidenced.
- **Cited evidence** > 1. 21 of 24 severity 1 and 2 incidents have post-mortems filed; 5 are past the ten-day window.
- **Gap** A clause is addressed but not completed.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `a663f99c5180`

### FND-INCIDENT-PM-PLATFORM-2026-02-1

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Platform Engineering - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `67e3d82cbc6e`

### FND-INCIDENT-PM-PLATFORM-2026-03-1

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-03  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. Contributing factors are recorded but 3 corrective actions have no named owner.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `1c6c30e9bcc3`

### FND-THIRD-PARTY-ACCESS-HR-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-HR-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - People Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `dab0bcf13101`

### FND-THIRD-PARTY-ACCESS-HR-2026-Q2-1

- **Check** CHK-THIRD-PARTY-ACCESS-HR-2026-Q2  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Evidence is dated 2025-11-22, 220 days before 2026-Q2 closed, exceeding the 100 day freshness window for Third-party access recertification.
- **Gap** Evidence is 220 days old against a 100 day limit.

### FND-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - Payments Processing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `866c956a18f1`

### FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** No evidence was submitted for 2026-Q1 against Third-party access recertification. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### FND-THIRD-PARTY-ACCESS-PROC-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by S. Haugen
- **Rationale** Evidence is dated 2025-08-24, 219 days before 2026-Q1 closed, exceeding the 100 day freshness window for Third-party access recertification.
- **Gap** Evidence is 219 days old against a 100 day limit.

### FND-THIRD-PARTY-ACCESS-PROC-2026-Q2-1

- **Check** CHK-THIRD-PARTY-ACCESS-PROC-2026-Q2  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by S. Haugen
- **Rationale** Evidence is dated 2025-11-22, 220 days before 2026-Q2 closed, exceeding the 100 day freshness window for Third-party access recertification.
- **Gap** Evidence is 220 days old against a 100 day limit.

### FND-TRAINING-CUSTOPS-2026-Q1-1

- **Check** CHK-TRAINING-CUSTOPS-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Threshold evaluation failed: completion_pct was 96.9 against a required at least 95.0; overdue_staff was 8 against a required at most 5.
- **Cited evidence** > "completion_pct": 96.9
- **Cited evidence** > "overdue_staff": 8
- **Gap** overdue_staff was 8, outside the required at most 5.

### FND-TRAINING-FINREP-2026-Q1-1

- **Check** CHK-TRAINING-FINREP-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** All thresholds met: completion_pct was 99.1 against a required at least 95.0; overdue_staff was 3 against a required at most 5.
- **Cited evidence** > "completion_pct": 99.1
- **Cited evidence** > "overdue_staff": 3

### FND-TRAINING-HR-2026-Q1-1

- **Check** CHK-TRAINING-HR-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** All thresholds met: completion_pct was 98.2 against a required at least 95.0; overdue_staff was 4 against a required at most 5.
- **Cited evidence** > "completion_pct": 98.2
- **Cited evidence** > "overdue_staff": 4

### FND-TRAINING-MKTG-2026-Q1-1

- **Check** CHK-TRAINING-MKTG-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by J. Alvarez
- **Rationale** Evidence is dated 2025-08-24, 219 days before 2026-Q1 closed, exceeding the 100 day freshness window for Mandatory compliance training completion.
- **Gap** Evidence is 219 days old against a 100 day limit.

### FND-TRAINING-PAYMENTS-2026-Q1-1

- **Check** CHK-TRAINING-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** All thresholds met: completion_pct was 99.5 against a required at least 95.0; overdue_staff was 2 against a required at most 5.
- **Cited evidence** > "completion_pct": 99.5
- **Cited evidence** > "overdue_staff": 2

### FND-TRAINING-PLATFORM-2026-Q1-1

- **Check** CHK-TRAINING-PLATFORM-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** Threshold evaluation failed: completion_pct was 93.6 against a required at least 95.0; overdue_staff was 1 against a required at most 5.
- **Cited evidence** > "completion_pct": 93.6
- **Cited evidence** > "overdue_staff": 1
- **Gap** completion_pct was 93.6, outside the required at least 95.0.

### FND-TRAINING-PROC-2026-Q1-1

- **Check** CHK-TRAINING-PROC-2026-Q1  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by S. Haugen
- **Rationale** Threshold evaluation failed: completion_pct was 77.0 against a required at least 95.0; overdue_staff was 50 against a required at most 5.
- **Cited evidence** > "completion_pct": 77.0
- **Cited evidence** > "overdue_staff": 50
- **Gap** completion_pct was 77.0, outside the required at least 95.0.
- **Gap** overdue_staff was 50, outside the required at most 5.

## 4. Action register

### ACT-ACCESS-EXPORT-PAYMENTS-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-ACCESS-EXPORT-PAYMENTS-2026-Q1-1 (gap, severity 4.292 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-05-12
- **History** raised (L. Okafor) → assigned (L. Okafor)

### ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 — resolved

- **Raised** 2026-04-28 from FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 (gap, severity 3.433 high)  
- **Owner** R. Mehta (Customer Operations) · due 2026-05-12
- **Remediation submitted** EV-SUB-UI-0317
- **Re-assessed** compliant
- **Closed** 2026-04-28 — Remediation accepted. FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-2 supersedes FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1: gap -> compliant, decided by s3_model.
- **History** raised (R. Mehta) → assigned (R. Mehta) → in_progress (R. Mehta) → remediation_submitted (R. Mehta) → reassessed (R. Mehta) → resolved (R. Mehta)

### ACT-ACCESS-REVIEW-HR-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-ACCESS-REVIEW-HR-2026-Q1-1 (gap, severity 2.575 medium)  
- **Owner** D. Ferreira (People Operations) · due 2026-05-28
- **History** raised (D. Ferreira) → assigned (D. Ferreira)

### ACT-ACCESS-REVIEW-MKTG-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-ACCESS-REVIEW-MKTG-2026-Q1-1 (gap, severity 1.717 medium)  
- **Owner** J. Alvarez (Marketing) · due 2026-05-28
- **History** raised (J. Alvarez) → assigned (J. Alvarez)

### ACT-ACCESS-REVIEW-PAYMENTS-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-ACCESS-REVIEW-PAYMENTS-2026-Q1-1 (overdue, severity 4.12 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-05-12
- **History** raised (L. Okafor) → assigned (L. Okafor)

### ACT-BACKUP-VERIFY-CUSTOPS-2026-01 — escalated

- **Raised** 2026-02-27 from FND-BACKUP-VERIFY-CUSTOPS-2026-01-1 (overdue, severity 2.72 medium)  
- **Owner** R. Mehta (Customer Operations) · due 2026-03-29
- **History** raised (R. Mehta) → assigned (R. Mehta) → escalated (Group Compliance)

### ACT-BACKUP-VERIFY-CUSTOPS-2026-02 — escalated

- **Raised** 2026-03-29 from FND-BACKUP-VERIFY-CUSTOPS-2026-02-1 (gap, severity 3.467 high)  
- **Owner** R. Mehta (Customer Operations) · due 2026-04-12
- **History** raised (R. Mehta) → assigned (R. Mehta) → escalated (Group Compliance)

### ACT-BACKUP-VERIFY-PAYMENTS-2026-02 — escalated

- **Raised** 2026-03-29 from FND-BACKUP-VERIFY-PAYMENTS-2026-02-1 (overdue, severity 4.16 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-04-12
- **History** raised (L. Okafor) → assigned (L. Okafor) → escalated (Group Compliance)

### ACT-BACKUP-VERIFY-PLATFORM-2026-03 — assigned

- **Raised** 2026-04-28 from FND-BACKUP-VERIFY-PLATFORM-2026-03-1 (gap, severity 5.15 high)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-05-12
- **History** raised (N. Iyer) → assigned (N. Iyer)

### ACT-CHANGE-MGMT-CUSTOPS-2026-03 — assigned

- **Raised** 2026-04-28 from FND-CHANGE-MGMT-CUSTOPS-2026-03-1 (gap, severity 1.831 medium)  
- **Owner** R. Mehta (Customer Operations) · due 2026-05-28
- **History** raised (R. Mehta) → assigned (R. Mehta)

### ACT-CHANGE-MGMT-FINREP-2026-02 — assigned

- **Raised** 2026-03-29 from FND-CHANGE-MGMT-FINREP-2026-02-1 (gap, severity 1.387 low)  
- **Owner** A. Novak (Finance) · due 2026-05-28
- **History** raised (A. Novak) → assigned (A. Novak)

### ACT-CHANGE-MGMT-FINREP-2026-03 — assigned

- **Raised** 2026-04-28 from FND-CHANGE-MGMT-FINREP-2026-03-1 (gap, severity 1.831 medium)  
- **Owner** A. Novak (Finance) · due 2026-05-28
- **History** raised (A. Novak) → assigned (A. Novak)

### ACT-CHANGE-MGMT-HR-2026-01 — assigned

- **Raised** 2026-02-27 from FND-CHANGE-MGMT-HR-2026-01-1 (overdue, severity 1.36 low)  
- **Owner** D. Ferreira (People Operations) · due 2026-04-28
- **History** raised (D. Ferreira) → assigned (D. Ferreira)

### ACT-CHANGE-MGMT-HR-2026-03 — assigned

- **Raised** 2026-04-28 from FND-CHANGE-MGMT-HR-2026-03-1 (gap, severity 1.717 medium)  
- **Owner** D. Ferreira (People Operations) · due 2026-05-28
- **History** raised (D. Ferreira) → assigned (D. Ferreira)

### ACT-CHANGE-MGMT-MKTG-2026-01 — assigned

- **Raised** 2026-02-27 from FND-CHANGE-MGMT-MKTG-2026-01-1 (overdue, severity 0.907 low)  
- **Owner** J. Alvarez (Marketing) · due 2026-04-28
- **History** raised (J. Alvarez) → assigned (J. Alvarez)

### ACT-CHANGE-MGMT-PAYMENTS-2026-02 — escalated

- **Raised** 2026-03-29 from FND-CHANGE-MGMT-PAYMENTS-2026-02-1 (gap, severity 3.467 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-04-12
- **History** raised (L. Okafor) → assigned (L. Okafor) → escalated (Group Compliance)

### ACT-CHANGE-MGMT-PAYMENTS-2026-03 — assigned

- **Raised** 2026-04-28 from FND-CHANGE-MGMT-PAYMENTS-2026-03-1 (overdue, severity 2.747 medium)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-05-28
- **History** raised (L. Okafor) → assigned (L. Okafor)

### ACT-CHANGE-MGMT-PLATFORM-2026-01 — escalated

- **Raised** 2026-02-27 from FND-CHANGE-MGMT-PLATFORM-2026-01-1 (overdue, severity 2.72 medium)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-03-29
- **History** raised (N. Iyer) → assigned (N. Iyer) → escalated (Group Compliance)

### ACT-CHANGE-MGMT-PLATFORM-2026-03 — assigned

- **Raised** 2026-04-28 from FND-CHANGE-MGMT-PLATFORM-2026-03-1 (gap, severity 3.433 high)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-05-12
- **History** raised (N. Iyer) → assigned (N. Iyer)

### ACT-CRYPTO-KEY-HR-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-CRYPTO-KEY-HR-2026-Q1-1 (overdue, severity 2.06 medium)  
- **Owner** D. Ferreira (People Operations) · due 2026-05-28
- **History** raised (D. Ferreira) → assigned (D. Ferreira)

### ACT-CRYPTO-KEY-MKTG-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-CRYPTO-KEY-MKTG-2026-Q1-1 (gap, severity 1.373 low)  
- **Owner** J. Alvarez (Marketing) · due 2026-06-27
- **History** raised (J. Alvarez) → assigned (J. Alvarez)

### ACT-CRYPTO-KEY-PAYMENTS-2026-Q1 — escalated

- **Raised** 2026-01-28 from FND-CRYPTO-KEY-PAYMENTS-2026-Q1-1 (gap, severity 4.5 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-02-11
- **History** raised (L. Okafor) → assigned (L. Okafor) → escalated (Group Compliance)

### ACT-CUST-COMPLAINTS-CUSTOPS-2026-02 — assigned

- **Raised** 2026-03-29 from FND-CUST-COMPLAINTS-CUSTOPS-2026-02-1 (overdue, severity 1.387 low)  
- **Owner** R. Mehta (Customer Operations) · due 2026-05-28
- **History** raised (R. Mehta) → assigned (R. Mehta)

### ACT-CUST-COMPLAINTS-CUSTOPS-2026-03 — assigned

- **Raised** 2026-04-28 from FND-CUST-COMPLAINTS-CUSTOPS-2026-03-1 (gap, severity 1.373 low)  
- **Owner** R. Mehta (Customer Operations) · due 2026-06-27
- **History** raised (R. Mehta) → assigned (R. Mehta)

### ACT-CUST-COMPLAINTS-MKTG-2026-01 — escalated

- **Raised** 2026-01-28 from FND-CUST-COMPLAINTS-MKTG-2026-01-1 (gap, severity 0.75 low)  
- **Owner** J. Alvarez (Marketing) · due 2026-03-29
- **History** raised (J. Alvarez) → assigned (J. Alvarez) → escalated (Group Compliance)

### ACT-DATA-RETENTION-CUSTOPS-2026-Q1 — escalated

- **Raised** 2026-01-28 from FND-DATA-RETENTION-CUSTOPS-2026-Q1-1 (gap, severity 3.0 high)  
- **Owner** R. Mehta (Customer Operations) · due 2026-02-11
- **History** raised (R. Mehta) → assigned (R. Mehta) → escalated (Group Compliance)

### ACT-DATA-RETENTION-HR-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-DATA-RETENTION-HR-2026-Q1-1 (gap, severity 2.575 medium)  
- **Owner** D. Ferreira (People Operations) · due 2026-05-28
- **History** raised (D. Ferreira) → assigned (D. Ferreira)

### ACT-DATA-RETENTION-MKTG-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-DATA-RETENTION-MKTG-2026-Q1-1 (gap, severity 1.717 medium)  
- **Owner** J. Alvarez (Marketing) · due 2026-05-28
- **History** raised (J. Alvarez) → assigned (J. Alvarez)

### ACT-DATA-RETENTION-PAYMENTS-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-DATA-RETENTION-PAYMENTS-2026-Q1-1 (overdue, severity 4.12 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-05-12
- **History** raised (L. Okafor) → assigned (L. Okafor)

### ACT-DPIA-MKTG-2026 — escalated

- **Raised** 2026-01-28 from FND-DPIA-MKTG-2026-1 (gap, severity 1.25 low)  
- **Owner** J. Alvarez (Marketing) · due 2026-03-29
- **History** raised (J. Alvarez) → assigned (J. Alvarez) → escalated (Group Compliance)

### ACT-INCIDENT-PM-CUSTOPS-2026-02 — assigned

- **Raised** 2026-03-29 from FND-INCIDENT-PM-CUSTOPS-2026-02-1 (gap, severity 1.733 medium)  
- **Owner** R. Mehta (Customer Operations) · due 2026-04-28
- **History** raised (R. Mehta) → assigned (R. Mehta)

### ACT-INCIDENT-PM-CUSTOPS-2026-03 — assigned

- **Raised** 2026-04-28 from FND-INCIDENT-PM-CUSTOPS-2026-03-1 (gap, severity 2.861 medium)  
- **Owner** R. Mehta (Customer Operations) · due 2026-05-28
- **History** raised (R. Mehta) → assigned (R. Mehta)

### ACT-INCIDENT-PM-FINREP-2026-03 — assigned

- **Raised** 2026-04-28 from FND-INCIDENT-PM-FINREP-2026-03-1 (gap, severity 2.861 medium)  
- **Owner** A. Novak (Finance) · due 2026-05-28
- **History** raised (A. Novak) → assigned (A. Novak)

### ACT-INCIDENT-PM-PAYMENTS-2026-01 — escalated

- **Raised** 2026-02-27 from FND-INCIDENT-PM-PAYMENTS-2026-01-1 (gap, severity 4.25 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-03-13
- **History** raised (L. Okafor) → assigned (L. Okafor) → escalated (Group Compliance)

### ACT-INCIDENT-PM-PAYMENTS-2026-02 — escalated

- **Raised** 2026-03-29 from FND-INCIDENT-PM-PAYMENTS-2026-02-1 (gap, severity 4.333 high)  
- **Owner** L. Okafor (Payments Engineering) · due 2026-04-12
- **History** raised (L. Okafor) → assigned (L. Okafor) → escalated (Group Compliance)

### ACT-INCIDENT-PM-PLATFORM-2026-01 — escalated

- **Raised** 2026-02-27 from FND-INCIDENT-PM-PLATFORM-2026-01-1 (gap, severity 2.55 medium)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-03-29
- **History** raised (N. Iyer) → assigned (N. Iyer) → escalated (Group Compliance)

### ACT-INCIDENT-PM-PLATFORM-2026-03 — assigned

- **Raised** 2026-04-28 from FND-INCIDENT-PM-PLATFORM-2026-03-1 (gap, severity 4.292 high)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-05-12
- **History** raised (N. Iyer) → assigned (N. Iyer)

### ACT-THIRD-PARTY-ACCESS-HR-2026-Q2 — assigned

- **Raised** 2026-04-28 from FND-THIRD-PARTY-ACCESS-HR-2026-Q2-1 (gap, severity 1.875 medium)  
- **Owner** D. Ferreira (People Operations) · due 2026-05-28
- **History** raised (D. Ferreira) → assigned (D. Ferreira)

### ACT-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1 (overdue, severity 3.433 high)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-05-12
- **History** raised (N. Iyer) → assigned (N. Iyer)

### ACT-THIRD-PARTY-ACCESS-PROC-2026-Q1 — escalated

- **Raised** 2026-01-28 from FND-THIRD-PARTY-ACCESS-PROC-2026-Q1-1 (gap, severity 1.875 medium)  
- **Owner** S. Haugen (Procurement) · due 2026-02-27
- **History** raised (S. Haugen) → assigned (S. Haugen) → escalated (Group Compliance)

### ACT-THIRD-PARTY-ACCESS-PROC-2026-Q2 — assigned

- **Raised** 2026-04-28 from FND-THIRD-PARTY-ACCESS-PROC-2026-Q2-1 (gap, severity 1.875 medium)  
- **Owner** S. Haugen (Procurement) · due 2026-05-28
- **History** raised (S. Haugen) → assigned (S. Haugen)

### ACT-TRAINING-CUSTOPS-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-TRAINING-CUSTOPS-2026-Q1-1 (gap, severity 1.717 medium)  
- **Owner** R. Mehta (Customer Operations) · due 2026-05-28
- **History** raised (R. Mehta) → assigned (R. Mehta)

### ACT-TRAINING-MKTG-2026-Q1 — escalated

- **Raised** 2026-01-28 from FND-TRAINING-MKTG-2026-Q1-1 (gap, severity 0.75 low)  
- **Owner** J. Alvarez (Marketing) · due 2026-03-29
- **History** raised (J. Alvarez) → assigned (J. Alvarez) → escalated (Group Compliance)

### ACT-TRAINING-PLATFORM-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-TRAINING-PLATFORM-2026-Q1-1 (gap, severity 2.575 medium)  
- **Owner** N. Iyer (Platform Engineering) · due 2026-05-28
- **History** raised (N. Iyer) → assigned (N. Iyer)

### ACT-TRAINING-PROC-2026-Q1 — assigned

- **Raised** 2026-04-28 from FND-TRAINING-PROC-2026-Q1-1 (gap, severity 1.287 low)  
- **Owner** S. Haugen (Procurement) · due 2026-06-27
- **History** raised (S. Haugen) → assigned (S. Haugen)

## 5. Method note

This pack was assembled from the append-only audit log and from nothing else. No
current-state table was read: not the findings, not the actions, not the check
register. Every figure, register and excerpt below was reconstructed by replaying
the events in sequence. If the log could not support a section, that section
would be missing rather than quietly filled in from elsewhere.

**How checks arise.** Each control carries an applicability expression over
process-area attributes. A control applies to an area when every attribute it
names matches; that decision is deterministic and involves no model. Instances
are generated from the control's frequency across the calendar and keyed on
control x area x period, so a cycle run twice produces no duplicates.

**How evidence is judged.** Four rules resolve what can be resolved before any
model is asked: no evidence, wrong document type, evidence unchanged since a
period already assessed, and evidence older than the control's freshness window.
Structured evidence is measured against numeric thresholds in code. Only
ambiguous prose reaches a model, and then exactly once, with the relevant
sections retrieved rather than the whole document. Every quoted span in a model
verdict is checked back against the source; a verdict citing text the document
does not contain is rejected rather than recorded.

**What is deterministic and what is not.** Applicability, scheduling,
escalation, the pre-screen rules, threshold evaluation, severity and routing are
code and produce the same answer every time. Only the assessment of prose
involves a model. Findings record which tier decided them, and rule-decided
findings carry a confidence of 1.0 because arithmetic against a stated threshold
is certain in a way a reading of a paragraph is not.

**Integrity.** Each log entry carries a sequence number, the hash of the entry
before it, and its own hash covering that link. Altering any entry breaks the
chain at that point and every point after. The verification result is printed on
the cover. This makes tampering evident; it does not make it impossible.

**Scope of the evidence.** This is a demonstration system running on a
synthetic, seeded corpus of a fictional organisation. The controls, areas,
evidence and outcomes are generated, not collected.


## 6. Chronological trail

725 events, in the order they were written.

| # | Timestamp | Actor | Owner | Event | Entity |
|---|---|---|---|---|---|
| 1 | 2026-01-01 00:00:00 | user | Group Risk Committee | exception_registered | ComplianceException:EXC-001 |
| 2 | 2026-01-01 00:00:01 | user | Chief Procurement Officer | exception_registered | ComplianceException:EXC-002 |
| 3 | 2026-01-01 00:00:02 | user | Finance Control Board | exception_registered | ComplianceException:EXC-003 |
| 4 | 2026-01-01 00:00:03 | user | Chief Information Security Officer | exception_registered | ComplianceException:EXC-004 |
| 5 | 2026-01-01 00:00:04 | system | synthetic generator | corpus_seeded | Corpus:20260831 |
| 6 | 2026-01-28 02:00:00 | user | user | cycle_started | Cycle:2026-01-28 |
| 7 | 2026-01-28 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1 |
| 8 | 2026-01-28 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1 |
| 9 | 2026-01-28 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 10 | 2026-01-28 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 11 | 2026-01-28 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 12 | 2026-01-28 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 13 | 2026-01-28 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BCP-TEST-CUSTOPS-2026 |
| 14 | 2026-01-28 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-BCP-TEST-CUSTOPS-2026 |
| 15 | 2026-01-28 02:00:09 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-01 |
| 16 | 2026-01-28 02:00:10 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-01 |
| 17 | 2026-01-28 02:00:11 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q1 |
| 18 | 2026-01-28 02:00:12 | system | R. Mehta | notification_logged | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q1 |
| 19 | 2026-01-28 02:00:13 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-01 |
| 20 | 2026-01-28 02:00:14 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-01 |
| 21 | 2026-01-28 02:00:15 | system | R. Mehta | check_instance_created | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 22 | 2026-01-28 02:00:16 | system | R. Mehta | notification_logged | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 23 | 2026-01-28 02:00:17 | system | R. Mehta | check_instance_created | CheckInstance:CHK-DPIA-CUSTOPS-2026 |
| 24 | 2026-01-28 02:00:18 | system | R. Mehta | notification_logged | CheckInstance:CHK-DPIA-CUSTOPS-2026 |
| 25 | 2026-01-28 02:00:19 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-01 |
| 26 | 2026-01-28 02:00:20 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-01 |
| 27 | 2026-01-28 02:00:21 | system | R. Mehta | check_instance_created | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q1 |
| 28 | 2026-01-28 02:00:22 | system | R. Mehta | notification_logged | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q1 |
| 29 | 2026-01-28 02:00:23 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-01 |
| 30 | 2026-01-28 02:00:24 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-01 |
| 31 | 2026-01-28 02:00:25 | system | A. Novak | check_instance_created | CheckInstance:CHK-BCP-TEST-FINREP-2026 |
| 32 | 2026-01-28 02:00:26 | system | A. Novak | notification_logged | CheckInstance:CHK-BCP-TEST-FINREP-2026 |
| 33 | 2026-01-28 02:00:27 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-01 |
| 34 | 2026-01-28 02:00:28 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-01 |
| 35 | 2026-01-28 02:00:29 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-01 |
| 36 | 2026-01-28 02:00:30 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-01 |
| 37 | 2026-01-28 02:00:31 | system | A. Novak | check_instance_created | CheckInstance:CHK-TRAINING-FINREP-2026-Q1 |
| 38 | 2026-01-28 02:00:32 | system | A. Novak | notification_logged | CheckInstance:CHK-TRAINING-FINREP-2026-Q1 |
| 39 | 2026-01-28 02:00:33 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 40 | 2026-01-28 02:00:34 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 41 | 2026-01-28 02:00:35 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q1 |
| 42 | 2026-01-28 02:00:36 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q1 |
| 43 | 2026-01-28 02:00:37 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 44 | 2026-01-28 02:00:38 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 45 | 2026-01-28 02:00:39 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 46 | 2026-01-28 02:00:40 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 47 | 2026-01-28 02:00:41 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q1 |
| 48 | 2026-01-28 02:00:42 | system | D. Ferreira | notification_logged | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q1 |
| 49 | 2026-01-28 02:00:43 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-DPIA-HR-2026 |
| 50 | 2026-01-28 02:00:44 | system | D. Ferreira | notification_logged | CheckInstance:CHK-DPIA-HR-2026 |
| 51 | 2026-01-28 02:00:45 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-HR-2026 |
| 52 | 2026-01-28 02:00:46 | system | D. Ferreira | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-HR-2026 |
| 53 | 2026-01-28 02:00:47 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q1 |
| 54 | 2026-01-28 02:00:48 | system | D. Ferreira | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q1 |
| 55 | 2026-01-28 02:00:49 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-TRAINING-HR-2026-Q1 |
| 56 | 2026-01-28 02:00:50 | system | D. Ferreira | notification_logged | CheckInstance:CHK-TRAINING-HR-2026-Q1 |
| 57 | 2026-01-28 02:00:51 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-VENDOR-DD-HR-2026 |
| 58 | 2026-01-28 02:00:52 | system | D. Ferreira | notification_logged | CheckInstance:CHK-VENDOR-DD-HR-2026 |
| 59 | 2026-01-28 02:00:53 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q1 |
| 60 | 2026-01-28 02:00:54 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q1 |
| 61 | 2026-01-28 02:00:55 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q1 |
| 62 | 2026-01-28 02:00:56 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q1 |
| 63 | 2026-01-28 02:00:57 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 64 | 2026-01-28 02:00:58 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 65 | 2026-01-28 02:00:59 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q1 |
| 66 | 2026-01-28 02:01:00 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q1 |
| 67 | 2026-01-28 02:01:01 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-01 |
| 68 | 2026-01-28 02:01:02 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-01 |
| 69 | 2026-01-28 02:01:03 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q1 |
| 70 | 2026-01-28 02:01:04 | system | J. Alvarez | notification_logged | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q1 |
| 71 | 2026-01-28 02:01:05 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-DPIA-MKTG-2026 |
| 72 | 2026-01-28 02:01:06 | system | J. Alvarez | notification_logged | CheckInstance:CHK-DPIA-MKTG-2026 |
| 73 | 2026-01-28 02:01:07 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-MKTG-2026 |
| 74 | 2026-01-28 02:01:08 | system | J. Alvarez | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-MKTG-2026 |
| 75 | 2026-01-28 02:01:09 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-TRAINING-MKTG-2026-Q1 |
| 76 | 2026-01-28 02:01:10 | system | J. Alvarez | notification_logged | CheckInstance:CHK-TRAINING-MKTG-2026-Q1 |
| 77 | 2026-01-28 02:01:11 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-VENDOR-DD-MKTG-2026 |
| 78 | 2026-01-28 02:01:12 | system | J. Alvarez | notification_logged | CheckInstance:CHK-VENDOR-DD-MKTG-2026 |
| 79 | 2026-01-28 02:01:13 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 80 | 2026-01-28 02:01:14 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 81 | 2026-01-28 02:01:15 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 82 | 2026-01-28 02:01:16 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 83 | 2026-01-28 02:01:17 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-01 |
| 84 | 2026-01-28 02:01:18 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-01 |
| 85 | 2026-01-28 02:01:19 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BCP-TEST-PAYMENTS-2026 |
| 86 | 2026-01-28 02:01:20 | system | L. Okafor | notification_logged | CheckInstance:CHK-BCP-TEST-PAYMENTS-2026 |
| 87 | 2026-01-28 02:01:21 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 88 | 2026-01-28 02:01:22 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 89 | 2026-01-28 02:01:23 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 90 | 2026-01-28 02:01:24 | system | L. Okafor | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 91 | 2026-01-28 02:01:25 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-01 |
| 92 | 2026-01-28 02:01:26 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-01 |
| 93 | 2026-01-28 02:01:27 | system | L. Okafor | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 94 | 2026-01-28 02:01:28 | system | L. Okafor | notification_logged | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 95 | 2026-01-28 02:01:29 | system | L. Okafor | check_instance_created | CheckInstance:CHK-DPIA-PAYMENTS-2026 |
| 96 | 2026-01-28 02:01:30 | system | L. Okafor | notification_logged | CheckInstance:CHK-DPIA-PAYMENTS-2026 |
| 97 | 2026-01-28 02:01:31 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-01 |
| 98 | 2026-01-28 02:01:32 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-01 |
| 99 | 2026-01-28 02:01:33 | system | L. Okafor | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PAYMENTS-2026 |
| 100 | 2026-01-28 02:01:34 | system | L. Okafor | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PAYMENTS-2026 |
| 101 | 2026-01-28 02:01:35 | system | L. Okafor | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1 |
| 102 | 2026-01-28 02:01:36 | system | L. Okafor | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1 |
| 103 | 2026-01-28 02:01:37 | system | L. Okafor | check_instance_created | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q1 |
| 104 | 2026-01-28 02:01:38 | system | L. Okafor | notification_logged | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q1 |
| 105 | 2026-01-28 02:01:39 | system | L. Okafor | check_instance_created | CheckInstance:CHK-VENDOR-DD-PAYMENTS-2026 |
| 106 | 2026-01-28 02:01:40 | system | L. Okafor | notification_logged | CheckInstance:CHK-VENDOR-DD-PAYMENTS-2026 |
| 107 | 2026-01-28 02:01:41 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-01 |
| 108 | 2026-01-28 02:01:42 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-01 |
| 109 | 2026-01-28 02:01:43 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 110 | 2026-01-28 02:01:44 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 111 | 2026-01-28 02:01:45 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 112 | 2026-01-28 02:01:46 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 113 | 2026-01-28 02:01:47 | system | N. Iyer | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PLATFORM-2026 |
| 114 | 2026-01-28 02:01:48 | system | N. Iyer | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PLATFORM-2026 |
| 115 | 2026-01-28 02:01:49 | system | N. Iyer | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 116 | 2026-01-28 02:01:50 | system | N. Iyer | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 117 | 2026-01-28 02:01:51 | system | N. Iyer | check_instance_created | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q1 |
| 118 | 2026-01-28 02:01:52 | system | N. Iyer | notification_logged | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q1 |
| 119 | 2026-01-28 02:01:53 | system | N. Iyer | check_instance_created | CheckInstance:CHK-VENDOR-DD-PLATFORM-2026 |
| 120 | 2026-01-28 02:01:54 | system | N. Iyer | notification_logged | CheckInstance:CHK-VENDOR-DD-PLATFORM-2026 |
| 121 | 2026-01-28 02:01:55 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-01 |
| 122 | 2026-01-28 02:01:56 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-01 |
| 123 | 2026-01-28 02:01:57 | system | S. Haugen | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PROC-2026 |
| 124 | 2026-01-28 02:01:58 | system | S. Haugen | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PROC-2026 |
| 125 | 2026-01-28 02:01:59 | system | S. Haugen | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 126 | 2026-01-28 02:02:00 | system | S. Haugen | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 127 | 2026-01-28 02:02:01 | system | S. Haugen | check_instance_created | CheckInstance:CHK-TRAINING-PROC-2026-Q1 |
| 128 | 2026-01-28 02:02:02 | system | S. Haugen | notification_logged | CheckInstance:CHK-TRAINING-PROC-2026-Q1 |
| 129 | 2026-01-28 02:02:03 | system | S. Haugen | check_instance_created | CheckInstance:CHK-VENDOR-DD-PROC-2026 |
| 130 | 2026-01-28 02:02:04 | system | S. Haugen | notification_logged | CheckInstance:CHK-VENDOR-DD-PROC-2026 |
| 131 | 2026-01-28 02:02:05 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 132 | 2026-01-28 02:02:06 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-01 |
| 133 | 2026-01-28 02:02:07 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 134 | 2026-01-28 02:02:08 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-DPIA-MKTG-2026 |
| 135 | 2026-01-28 02:02:09 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 136 | 2026-01-28 02:02:10 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-TRAINING-MKTG-2026-Q1 |
| 137 | 2026-01-28 02:02:11 | user | user | cycle_completed | Cycle:2026-01-28 |
| 138 | 2026-01-28 03:00:00 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0212 |
| 139 | 2026-01-28 03:00:01 | system | J. Alvarez | finding_recorded | Finding:FND-DPIA-MKTG-2026-1 |
| 140 | 2026-01-28 03:00:02 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0172 |
| 141 | 2026-01-28 03:00:03 | system | J. Alvarez | finding_recorded | Finding:FND-CUST-COMPLAINTS-MKTG-2026-01-1 |
| 142 | 2026-01-28 03:00:04 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0158 |
| 143 | 2026-01-28 03:00:05 | system | L. Okafor | finding_recorded | Finding:FND-CRYPTO-KEY-PAYMENTS-2026-Q1-1 |
| 144 | 2026-01-28 03:00:06 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0196 |
| 145 | 2026-01-28 03:00:07 | system | R. Mehta | finding_recorded | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1-1 |
| 146 | 2026-01-28 03:00:08 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0276 |
| 147 | 2026-01-28 03:00:09 | system | S. Haugen | finding_recorded | Finding:FND-THIRD-PARTY-ACCESS-PROC-2026-Q1-1 |
| 148 | 2026-01-28 03:00:10 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0291 |
| 149 | 2026-01-28 03:00:11 | system | J. Alvarez | finding_recorded | Finding:FND-TRAINING-MKTG-2026-Q1-1 |
| 150 | 2026-01-28 03:00:12 | system | prescreen | prescreen_completed | Cycle:2026-01-28 |
| 151 | 2026-01-28 05:00:00 | system | L. Okafor | flag_raised | Flag:FLG-GAP-FND-CRYPTO-KEY-PAYMENTS-2026-Q1-1 |
| 152 | 2026-01-28 05:00:01 | system | L. Okafor | action_raised | Action:ACT-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 153 | 2026-01-28 05:00:02 | system | L. Okafor | action_assigned | Action:ACT-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 154 | 2026-01-28 05:00:03 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-FND-CUST-COMPLAINTS-MKTG-2026-01-1 |
| 155 | 2026-01-28 05:00:04 | system | J. Alvarez | action_raised | Action:ACT-CUST-COMPLAINTS-MKTG-2026-01 |
| 156 | 2026-01-28 05:00:05 | system | J. Alvarez | action_assigned | Action:ACT-CUST-COMPLAINTS-MKTG-2026-01 |
| 157 | 2026-01-28 05:00:06 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-DATA-RETENTION-CUSTOPS-2026-Q1-1 |
| 158 | 2026-01-28 05:00:07 | system | R. Mehta | action_raised | Action:ACT-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 159 | 2026-01-28 05:00:08 | system | R. Mehta | action_assigned | Action:ACT-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 160 | 2026-01-28 05:00:09 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-FND-DPIA-MKTG-2026-1 |
| 161 | 2026-01-28 05:00:10 | system | J. Alvarez | action_raised | Action:ACT-DPIA-MKTG-2026 |
| 162 | 2026-01-28 05:00:11 | system | J. Alvarez | action_assigned | Action:ACT-DPIA-MKTG-2026 |
| 163 | 2026-01-28 05:00:12 | system | S. Haugen | flag_raised | Flag:FLG-GAP-FND-THIRD-PARTY-ACCESS-PROC-2026-Q1-1 |
| 164 | 2026-01-28 05:00:13 | system | S. Haugen | action_raised | Action:ACT-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 165 | 2026-01-28 05:00:14 | system | S. Haugen | action_assigned | Action:ACT-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 166 | 2026-01-28 05:00:15 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-FND-TRAINING-MKTG-2026-Q1-1 |
| 167 | 2026-01-28 05:00:16 | system | J. Alvarez | action_raised | Action:ACT-TRAINING-MKTG-2026-Q1 |
| 168 | 2026-01-28 05:00:17 | system | J. Alvarez | action_assigned | Action:ACT-TRAINING-MKTG-2026-Q1 |
| 169 | 2026-01-28 05:00:18 | system | flagging | flagging_completed | Cycle:2026-01-28 |
| 170 | 2026-02-27 02:00:00 | user | user | cycle_started | Cycle:2026-02-27 |
| 171 | 2026-02-27 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 172 | 2026-02-27 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 173 | 2026-02-27 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-02 |
| 174 | 2026-02-27 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-02 |
| 175 | 2026-02-27 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 176 | 2026-02-27 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 177 | 2026-02-27 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-02 |
| 178 | 2026-02-27 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-02 |
| 179 | 2026-02-27 02:00:09 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-02 |
| 180 | 2026-02-27 02:00:10 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-02 |
| 181 | 2026-02-27 02:00:11 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 182 | 2026-02-27 02:00:12 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 183 | 2026-02-27 02:00:13 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 184 | 2026-02-27 02:00:14 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 185 | 2026-02-27 02:00:15 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-02 |
| 186 | 2026-02-27 02:00:16 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-02 |
| 187 | 2026-02-27 02:00:17 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 188 | 2026-02-27 02:00:18 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 189 | 2026-02-27 02:00:19 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-02 |
| 190 | 2026-02-27 02:00:20 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-02 |
| 191 | 2026-02-27 02:00:21 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 192 | 2026-02-27 02:00:22 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 193 | 2026-02-27 02:00:23 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-02 |
| 194 | 2026-02-27 02:00:24 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-02 |
| 195 | 2026-02-27 02:00:25 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-02 |
| 196 | 2026-02-27 02:00:26 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-02 |
| 197 | 2026-02-27 02:00:27 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-02 |
| 198 | 2026-02-27 02:00:28 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-02 |
| 199 | 2026-02-27 02:00:29 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-02 |
| 200 | 2026-02-27 02:00:30 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-02 |
| 201 | 2026-02-27 02:00:31 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-02 |
| 202 | 2026-02-27 02:00:32 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-02 |
| 203 | 2026-02-27 02:00:33 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 204 | 2026-02-27 02:00:34 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 205 | 2026-02-27 02:00:35 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-02 |
| 206 | 2026-02-27 02:00:36 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-02 |
| 207 | 2026-02-27 02:00:37 | system | R. Mehta | check_instance_overdue | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 208 | 2026-02-27 02:00:38 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 209 | 2026-02-27 02:00:39 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-01 |
| 210 | 2026-02-27 02:00:40 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-01 |
| 211 | 2026-02-27 02:00:41 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-01 |
| 212 | 2026-02-27 02:00:42 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-01 |
| 213 | 2026-02-27 02:00:43 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-01 |
| 214 | 2026-02-27 02:00:44 | system | D. Ferreira | check_instance_overdue | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 215 | 2026-02-27 02:00:45 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 216 | 2026-02-27 02:00:46 | system | J. Alvarez | check_instance_overdue | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 217 | 2026-02-27 02:00:47 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 218 | 2026-02-27 02:00:48 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 219 | 2026-02-27 02:00:49 | system | N. Iyer | check_instance_overdue | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 220 | 2026-02-27 02:00:50 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 221 | 2026-02-27 02:00:51 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-01 |
| 222 | 2026-02-27 02:00:52 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-01 |
| 223 | 2026-02-27 02:00:53 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-01 |
| 224 | 2026-02-27 02:00:54 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-01 |
| 225 | 2026-02-27 02:00:55 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-01 |
| 226 | 2026-02-27 02:00:56 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-01 |
| 227 | 2026-02-27 02:00:57 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 228 | 2026-02-27 02:00:58 | user | user | cycle_completed | Cycle:2026-02-27 |
| 229 | 2026-02-27 03:00:00 | system | R. Mehta | finding_recorded | Finding:FND-BACKUP-VERIFY-CUSTOPS-2026-01-1 |
| 230 | 2026-02-27 03:00:01 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0039 |
| 231 | 2026-02-27 03:00:02 | system | A. Novak | finding_recorded | Finding:FND-BACKUP-VERIFY-FINREP-2026-01-1 |
| 232 | 2026-02-27 03:00:03 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0049 |
| 233 | 2026-02-27 03:00:04 | system | L. Okafor | finding_recorded | Finding:FND-BACKUP-VERIFY-PAYMENTS-2026-01-1 |
| 234 | 2026-02-27 03:00:05 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0059 |
| 235 | 2026-02-27 03:00:06 | system | N. Iyer | finding_recorded | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-01-1 |
| 236 | 2026-02-27 03:00:07 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0073 |
| 237 | 2026-02-27 03:00:08 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0084 |
| 238 | 2026-02-27 03:00:09 | system | D. Ferreira | finding_recorded | Finding:FND-CHANGE-MGMT-HR-2026-01-1 |
| 239 | 2026-02-27 03:00:10 | system | J. Alvarez | finding_recorded | Finding:FND-CHANGE-MGMT-MKTG-2026-01-1 |
| 240 | 2026-02-27 03:00:11 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0116 |
| 241 | 2026-02-27 03:00:12 | system | N. Iyer | finding_recorded | Finding:FND-CHANGE-MGMT-PLATFORM-2026-01-1 |
| 242 | 2026-02-27 03:00:13 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0137 |
| 243 | 2026-02-27 03:00:14 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0162 |
| 244 | 2026-02-27 03:00:15 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0184 |
| 245 | 2026-02-27 03:00:16 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0214 |
| 246 | 2026-02-27 03:00:17 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0225 |
| 247 | 2026-02-27 03:00:18 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0237 |
| 248 | 2026-02-27 03:00:19 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0248 |
| 249 | 2026-02-27 03:00:20 | system | prescreen | prescreen_completed | Cycle:2026-02-27 |
| 250 | 2026-02-27 04:00:00 | ai | R. Mehta | finding_recorded | Finding:FND-CHANGE-MGMT-CUSTOPS-2026-01-1 |
| 251 | 2026-02-27 04:00:01 | ai | A. Novak | finding_recorded | Finding:FND-CHANGE-MGMT-FINREP-2026-01-1 |
| 252 | 2026-02-27 04:00:02 | ai | L. Okafor | finding_recorded | Finding:FND-CHANGE-MGMT-PAYMENTS-2026-01-1 |
| 253 | 2026-02-27 04:00:03 | ai | S. Haugen | finding_recorded | Finding:FND-CHANGE-MGMT-PROC-2026-01-1 |
| 254 | 2026-02-27 04:00:04 | ai | R. Mehta | finding_recorded | Finding:FND-CUST-COMPLAINTS-CUSTOPS-2026-01-1 |
| 255 | 2026-02-27 04:00:05 | ai | L. Okafor | finding_recorded | Finding:FND-CUST-COMPLAINTS-PAYMENTS-2026-01-1 |
| 256 | 2026-02-27 04:00:06 | ai | R. Mehta | finding_recorded | Finding:FND-INCIDENT-PM-CUSTOPS-2026-01-1 |
| 257 | 2026-02-27 04:00:07 | ai | A. Novak | finding_recorded | Finding:FND-INCIDENT-PM-FINREP-2026-01-1 |
| 258 | 2026-02-27 04:00:08 | ai | L. Okafor | finding_recorded | Finding:FND-INCIDENT-PM-PAYMENTS-2026-01-1 |
| 259 | 2026-02-27 04:00:09 | ai | N. Iyer | finding_recorded | Finding:FND-INCIDENT-PM-PLATFORM-2026-01-1 |
| 260 | 2026-02-27 04:00:10 | system | assessor | assessment_completed | Cycle:2026-02-27 |
| 261 | 2026-02-27 05:00:00 | system | R. Mehta | flag_raised | Flag:FLG-OVERDUE-FND-BACKUP-VERIFY-CUSTOPS-2026-01-1 |
| 262 | 2026-02-27 05:00:01 | system | R. Mehta | action_raised | Action:ACT-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 263 | 2026-02-27 05:00:02 | system | R. Mehta | action_assigned | Action:ACT-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 264 | 2026-02-27 05:00:03 | system | D. Ferreira | flag_raised | Flag:FLG-OVERDUE-FND-CHANGE-MGMT-HR-2026-01-1 |
| 265 | 2026-02-27 05:00:04 | system | D. Ferreira | action_raised | Action:ACT-CHANGE-MGMT-HR-2026-01 |
| 266 | 2026-02-27 05:00:05 | system | D. Ferreira | action_assigned | Action:ACT-CHANGE-MGMT-HR-2026-01 |
| 267 | 2026-02-27 05:00:06 | system | J. Alvarez | flag_raised | Flag:FLG-OVERDUE-FND-CHANGE-MGMT-MKTG-2026-01-1 |
| 268 | 2026-02-27 05:00:07 | system | J. Alvarez | action_raised | Action:ACT-CHANGE-MGMT-MKTG-2026-01 |
| 269 | 2026-02-27 05:00:08 | system | J. Alvarez | action_assigned | Action:ACT-CHANGE-MGMT-MKTG-2026-01 |
| 270 | 2026-02-27 05:00:09 | system | N. Iyer | flag_raised | Flag:FLG-OVERDUE-FND-CHANGE-MGMT-PLATFORM-2026-01-1 |
| 271 | 2026-02-27 05:00:10 | system | N. Iyer | action_raised | Action:ACT-CHANGE-MGMT-PLATFORM-2026-01 |
| 272 | 2026-02-27 05:00:11 | system | N. Iyer | action_assigned | Action:ACT-CHANGE-MGMT-PLATFORM-2026-01 |
| 273 | 2026-02-27 05:00:12 | system | L. Okafor | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-PAYMENTS-2026-01-1 |
| 274 | 2026-02-27 05:00:13 | system | L. Okafor | action_raised | Action:ACT-INCIDENT-PM-PAYMENTS-2026-01 |
| 275 | 2026-02-27 05:00:14 | system | L. Okafor | action_assigned | Action:ACT-INCIDENT-PM-PAYMENTS-2026-01 |
| 276 | 2026-02-27 05:00:15 | system | N. Iyer | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-PLATFORM-2026-01-1 |
| 277 | 2026-02-27 05:00:16 | system | N. Iyer | action_raised | Action:ACT-INCIDENT-PM-PLATFORM-2026-01 |
| 278 | 2026-02-27 05:00:17 | system | N. Iyer | action_assigned | Action:ACT-INCIDENT-PM-PLATFORM-2026-01 |
| 279 | 2026-02-27 05:00:18 | system | Group Compliance | action_escalated | Action:ACT-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 280 | 2026-02-27 05:00:19 | system | Group Compliance | action_escalated | Action:ACT-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 281 | 2026-02-27 05:00:20 | system | flagging | flagging_completed | Cycle:2026-02-27 |
| 282 | 2026-03-29 02:00:00 | user | user | cycle_started | Cycle:2026-03-29 |
| 283 | 2026-03-29 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-03 |
| 284 | 2026-03-29 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-03 |
| 285 | 2026-03-29 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-03 |
| 286 | 2026-03-29 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-03 |
| 287 | 2026-03-29 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 288 | 2026-03-29 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 289 | 2026-03-29 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-03 |
| 290 | 2026-03-29 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-03 |
| 291 | 2026-03-29 02:00:09 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-03 |
| 292 | 2026-03-29 02:00:10 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-03 |
| 293 | 2026-03-29 02:00:11 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-03 |
| 294 | 2026-03-29 02:00:12 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-03 |
| 295 | 2026-03-29 02:00:13 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-03 |
| 296 | 2026-03-29 02:00:14 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-03 |
| 297 | 2026-03-29 02:00:15 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-03 |
| 298 | 2026-03-29 02:00:16 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-03 |
| 299 | 2026-03-29 02:00:17 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-03 |
| 300 | 2026-03-29 02:00:18 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-03 |
| 301 | 2026-03-29 02:00:19 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-03 |
| 302 | 2026-03-29 02:00:20 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-03 |
| 303 | 2026-03-29 02:00:21 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-03 |
| 304 | 2026-03-29 02:00:22 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-03 |
| 305 | 2026-03-29 02:00:23 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 306 | 2026-03-29 02:00:24 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 307 | 2026-03-29 02:00:25 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-03 |
| 308 | 2026-03-29 02:00:26 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-03 |
| 309 | 2026-03-29 02:00:27 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-03 |
| 310 | 2026-03-29 02:00:28 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-03 |
| 311 | 2026-03-29 02:00:29 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-03 |
| 312 | 2026-03-29 02:00:30 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-03 |
| 313 | 2026-03-29 02:00:31 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-03 |
| 314 | 2026-03-29 02:00:32 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-03 |
| 315 | 2026-03-29 02:00:33 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-03 |
| 316 | 2026-03-29 02:00:34 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-03 |
| 317 | 2026-03-29 02:00:35 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-03 |
| 318 | 2026-03-29 02:00:36 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-03 |
| 319 | 2026-03-29 02:00:37 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 320 | 2026-03-29 02:00:38 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-02 |
| 321 | 2026-03-29 02:00:39 | system | L. Okafor | check_instance_overdue | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 322 | 2026-03-29 02:00:40 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 323 | 2026-03-29 02:00:41 | system | Head of Payments Engineering | check_instance_escalated | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 324 | 2026-03-29 02:00:42 | system | Head of Payments Engineering | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 325 | 2026-03-29 02:00:43 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-02 |
| 326 | 2026-03-29 02:00:44 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-02 |
| 327 | 2026-03-29 02:00:45 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 328 | 2026-03-29 02:00:46 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-HR-2026-02 |
| 329 | 2026-03-29 02:00:47 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 330 | 2026-03-29 02:00:48 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-02 |
| 331 | 2026-03-29 02:00:49 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-02 |
| 332 | 2026-03-29 02:00:50 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-02 |
| 333 | 2026-03-29 02:00:51 | system | R. Mehta | check_instance_overdue | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 334 | 2026-03-29 02:00:52 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 335 | 2026-03-29 02:00:53 | system | Head of Customer Operations | check_instance_escalated | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 336 | 2026-03-29 02:00:54 | system | Head of Customer Operations | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 337 | 2026-03-29 02:00:55 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-02 |
| 338 | 2026-03-29 02:00:56 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-02 |
| 339 | 2026-03-29 02:00:57 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-02 |
| 340 | 2026-03-29 02:00:58 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 341 | 2026-03-29 02:00:59 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-02 |
| 342 | 2026-03-29 02:01:00 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 343 | 2026-03-29 02:01:01 | user | user | cycle_completed | Cycle:2026-03-29 |
| 344 | 2026-03-29 03:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0030 |
| 345 | 2026-03-29 03:00:01 | system | R. Mehta | finding_recorded | Finding:FND-BACKUP-VERIFY-CUSTOPS-2026-02-1 |
| 346 | 2026-03-29 03:00:02 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0040 |
| 347 | 2026-03-29 03:00:03 | system | A. Novak | finding_recorded | Finding:FND-BACKUP-VERIFY-FINREP-2026-02-1 |
| 348 | 2026-03-29 03:00:04 | system | L. Okafor | finding_recorded | Finding:FND-BACKUP-VERIFY-PAYMENTS-2026-02-1 |
| 349 | 2026-03-29 03:00:05 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0060 |
| 350 | 2026-03-29 03:00:06 | system | N. Iyer | finding_recorded | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-02-1 |
| 351 | 2026-03-29 03:00:07 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0074 |
| 352 | 2026-03-29 03:00:08 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0085 |
| 353 | 2026-03-29 03:00:09 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0095 |
| 354 | 2026-03-29 03:00:10 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0105 |
| 355 | 2026-03-29 03:00:11 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0117 |
| 356 | 2026-03-29 03:00:12 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0127 |
| 357 | 2026-03-29 03:00:13 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0138 |
| 358 | 2026-03-29 03:00:14 | system | R. Mehta | finding_recorded | Finding:FND-CUST-COMPLAINTS-CUSTOPS-2026-02-1 |
| 359 | 2026-03-29 03:00:15 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0173 |
| 360 | 2026-03-29 03:00:16 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0185 |
| 361 | 2026-03-29 03:00:17 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0215 |
| 362 | 2026-03-29 03:00:18 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0226 |
| 363 | 2026-03-29 03:00:19 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0238 |
| 364 | 2026-03-29 03:00:20 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0249 |
| 365 | 2026-03-29 03:00:21 | system | prescreen | prescreen_completed | Cycle:2026-03-29 |
| 366 | 2026-03-29 04:00:00 | ai | R. Mehta | finding_recorded | Finding:FND-CHANGE-MGMT-CUSTOPS-2026-02-1 |
| 367 | 2026-03-29 04:00:01 | ai | A. Novak | finding_recorded | Finding:FND-CHANGE-MGMT-FINREP-2026-02-1 |
| 368 | 2026-03-29 04:00:02 | ai | D. Ferreira | finding_recorded | Finding:FND-CHANGE-MGMT-HR-2026-02-1 |
| 369 | 2026-03-29 04:00:03 | ai | J. Alvarez | finding_recorded | Finding:FND-CHANGE-MGMT-MKTG-2026-02-1 |
| 370 | 2026-03-29 04:00:04 | ai | L. Okafor | finding_recorded | Finding:FND-CHANGE-MGMT-PAYMENTS-2026-02-1 |
| 371 | 2026-03-29 04:00:05 | ai | N. Iyer | finding_recorded | Finding:FND-CHANGE-MGMT-PLATFORM-2026-02-1 |
| 372 | 2026-03-29 04:00:06 | ai | S. Haugen | finding_recorded | Finding:FND-CHANGE-MGMT-PROC-2026-02-1 |
| 373 | 2026-03-29 04:00:07 | ai | J. Alvarez | finding_recorded | Finding:FND-CUST-COMPLAINTS-MKTG-2026-02-1 |
| 374 | 2026-03-29 04:00:08 | ai | L. Okafor | finding_recorded | Finding:FND-CUST-COMPLAINTS-PAYMENTS-2026-02-1 |
| 375 | 2026-03-29 04:00:09 | ai | R. Mehta | finding_recorded | Finding:FND-INCIDENT-PM-CUSTOPS-2026-02-1 |
| 376 | 2026-03-29 04:00:10 | ai | A. Novak | finding_recorded | Finding:FND-INCIDENT-PM-FINREP-2026-02-1 |
| 377 | 2026-03-29 04:00:11 | ai | L. Okafor | finding_recorded | Finding:FND-INCIDENT-PM-PAYMENTS-2026-02-1 |
| 378 | 2026-03-29 04:00:12 | ai | N. Iyer | finding_recorded | Finding:FND-INCIDENT-PM-PLATFORM-2026-02-1 |
| 379 | 2026-03-29 04:00:13 | system | assessor | assessment_completed | Cycle:2026-03-29 |
| 380 | 2026-03-29 05:00:00 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-BACKUP-VERIFY-CUSTOPS-2026-02-1 |
| 381 | 2026-03-29 05:00:01 | system | R. Mehta | action_raised | Action:ACT-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 382 | 2026-03-29 05:00:02 | system | R. Mehta | action_assigned | Action:ACT-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 383 | 2026-03-29 05:00:03 | system | L. Okafor | flag_raised | Flag:FLG-OVERDUE-FND-BACKUP-VERIFY-PAYMENTS-2026-02-1 |
| 384 | 2026-03-29 05:00:04 | system | L. Okafor | action_raised | Action:ACT-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 385 | 2026-03-29 05:00:05 | system | L. Okafor | action_assigned | Action:ACT-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 386 | 2026-03-29 05:00:06 | system | A. Novak | flag_raised | Flag:FLG-GAP-FND-CHANGE-MGMT-FINREP-2026-02-1 |
| 387 | 2026-03-29 05:00:07 | system | A. Novak | action_raised | Action:ACT-CHANGE-MGMT-FINREP-2026-02 |
| 388 | 2026-03-29 05:00:08 | system | A. Novak | action_assigned | Action:ACT-CHANGE-MGMT-FINREP-2026-02 |
| 389 | 2026-03-29 05:00:09 | system | L. Okafor | flag_raised | Flag:FLG-GAP-FND-CHANGE-MGMT-PAYMENTS-2026-02-1 |
| 390 | 2026-03-29 05:00:10 | system | L. Okafor | action_raised | Action:ACT-CHANGE-MGMT-PAYMENTS-2026-02 |
| 391 | 2026-03-29 05:00:11 | system | L. Okafor | action_assigned | Action:ACT-CHANGE-MGMT-PAYMENTS-2026-02 |
| 392 | 2026-03-29 05:00:12 | system | R. Mehta | flag_raised | Flag:FLG-OVERDUE-FND-CUST-COMPLAINTS-CUSTOPS-2026-02-1 |
| 393 | 2026-03-29 05:00:13 | system | R. Mehta | action_raised | Action:ACT-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 394 | 2026-03-29 05:00:14 | system | R. Mehta | action_assigned | Action:ACT-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 395 | 2026-03-29 05:00:15 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-CUSTOPS-2026-02-1 |
| 396 | 2026-03-29 05:00:16 | system | R. Mehta | action_raised | Action:ACT-INCIDENT-PM-CUSTOPS-2026-02 |
| 397 | 2026-03-29 05:00:17 | system | R. Mehta | action_assigned | Action:ACT-INCIDENT-PM-CUSTOPS-2026-02 |
| 398 | 2026-03-29 05:00:18 | system | L. Okafor | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-PAYMENTS-2026-02-1 |
| 399 | 2026-03-29 05:00:19 | system | L. Okafor | action_raised | Action:ACT-INCIDENT-PM-PAYMENTS-2026-02 |
| 400 | 2026-03-29 05:00:20 | system | L. Okafor | action_assigned | Action:ACT-INCIDENT-PM-PAYMENTS-2026-02 |
| 401 | 2026-03-29 05:00:21 | system | Group Compliance | action_escalated | Action:ACT-INCIDENT-PM-PAYMENTS-2026-01 |
| 402 | 2026-03-29 05:00:22 | system | Group Compliance | action_escalated | Action:ACT-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 403 | 2026-03-29 05:00:23 | system | flagging | flagging_completed | Cycle:2026-03-29 |
| 404 | 2026-04-28 02:00:00 | user | user | cycle_started | Cycle:2026-04-28 |
| 405 | 2026-04-28 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q2 |
| 406 | 2026-04-28 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q2 |
| 407 | 2026-04-28 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q2 |
| 408 | 2026-04-28 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q2 |
| 409 | 2026-04-28 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-04 |
| 410 | 2026-04-28 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-04 |
| 411 | 2026-04-28 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-04 |
| 412 | 2026-04-28 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-04 |
| 413 | 2026-04-28 02:00:09 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q2 |
| 414 | 2026-04-28 02:00:10 | system | R. Mehta | notification_logged | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q2 |
| 415 | 2026-04-28 02:00:11 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-04 |
| 416 | 2026-04-28 02:00:12 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-04 |
| 417 | 2026-04-28 02:00:13 | system | R. Mehta | check_instance_created | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q2 |
| 418 | 2026-04-28 02:00:14 | system | R. Mehta | notification_logged | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q2 |
| 419 | 2026-04-28 02:00:15 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-04 |
| 420 | 2026-04-28 02:00:16 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-04 |
| 421 | 2026-04-28 02:00:17 | system | R. Mehta | check_instance_created | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q2 |
| 422 | 2026-04-28 02:00:18 | system | R. Mehta | notification_logged | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q2 |
| 423 | 2026-04-28 02:00:19 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-04 |
| 424 | 2026-04-28 02:00:20 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-04 |
| 425 | 2026-04-28 02:00:21 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-04 |
| 426 | 2026-04-28 02:00:22 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-04 |
| 427 | 2026-04-28 02:00:23 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-04 |
| 428 | 2026-04-28 02:00:24 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-04 |
| 429 | 2026-04-28 02:00:25 | system | A. Novak | check_instance_created | CheckInstance:CHK-TRAINING-FINREP-2026-Q2 |
| 430 | 2026-04-28 02:00:26 | system | A. Novak | notification_logged | CheckInstance:CHK-TRAINING-FINREP-2026-Q2 |
| 431 | 2026-04-28 02:00:27 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q2 |
| 432 | 2026-04-28 02:00:28 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q2 |
| 433 | 2026-04-28 02:00:29 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q2 |
| 434 | 2026-04-28 02:00:30 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q2 |
| 435 | 2026-04-28 02:00:31 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-04 |
| 436 | 2026-04-28 02:00:32 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-04 |
| 437 | 2026-04-28 02:00:33 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q2 |
| 438 | 2026-04-28 02:00:34 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q2 |
| 439 | 2026-04-28 02:00:35 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q2 |
| 440 | 2026-04-28 02:00:36 | system | D. Ferreira | notification_logged | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q2 |
| 441 | 2026-04-28 02:00:37 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 442 | 2026-04-28 02:00:38 | system | D. Ferreira | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 443 | 2026-04-28 02:00:39 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-TRAINING-HR-2026-Q2 |
| 444 | 2026-04-28 02:00:40 | system | D. Ferreira | notification_logged | CheckInstance:CHK-TRAINING-HR-2026-Q2 |
| 445 | 2026-04-28 02:00:41 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q2 |
| 446 | 2026-04-28 02:00:42 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q2 |
| 447 | 2026-04-28 02:00:43 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q2 |
| 448 | 2026-04-28 02:00:44 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q2 |
| 449 | 2026-04-28 02:00:45 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-04 |
| 450 | 2026-04-28 02:00:46 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-04 |
| 451 | 2026-04-28 02:00:47 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q2 |
| 452 | 2026-04-28 02:00:48 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q2 |
| 453 | 2026-04-28 02:00:49 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-04 |
| 454 | 2026-04-28 02:00:50 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-04 |
| 455 | 2026-04-28 02:00:51 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q2 |
| 456 | 2026-04-28 02:00:52 | system | J. Alvarez | notification_logged | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q2 |
| 457 | 2026-04-28 02:00:53 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-TRAINING-MKTG-2026-Q2 |
| 458 | 2026-04-28 02:00:54 | system | J. Alvarez | notification_logged | CheckInstance:CHK-TRAINING-MKTG-2026-Q2 |
| 459 | 2026-04-28 02:00:55 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q2 |
| 460 | 2026-04-28 02:00:56 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q2 |
| 461 | 2026-04-28 02:00:57 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q2 |
| 462 | 2026-04-28 02:00:58 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q2 |
| 463 | 2026-04-28 02:00:59 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-04 |
| 464 | 2026-04-28 02:01:00 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-04 |
| 465 | 2026-04-28 02:01:01 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-04 |
| 466 | 2026-04-28 02:01:02 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-04 |
| 467 | 2026-04-28 02:01:03 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q2 |
| 468 | 2026-04-28 02:01:04 | system | L. Okafor | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q2 |
| 469 | 2026-04-28 02:01:05 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-04 |
| 470 | 2026-04-28 02:01:06 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-04 |
| 471 | 2026-04-28 02:01:07 | system | L. Okafor | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q2 |
| 472 | 2026-04-28 02:01:08 | system | L. Okafor | notification_logged | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q2 |
| 473 | 2026-04-28 02:01:09 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-04 |
| 474 | 2026-04-28 02:01:10 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-04 |
| 475 | 2026-04-28 02:01:11 | system | L. Okafor | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q2 |
| 476 | 2026-04-28 02:01:12 | system | L. Okafor | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q2 |
| 477 | 2026-04-28 02:01:13 | system | L. Okafor | check_instance_created | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q2 |
| 478 | 2026-04-28 02:01:14 | system | L. Okafor | notification_logged | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q2 |
| 479 | 2026-04-28 02:01:15 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-04 |
| 480 | 2026-04-28 02:01:16 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-04 |
| 481 | 2026-04-28 02:01:17 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-04 |
| 482 | 2026-04-28 02:01:18 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-04 |
| 483 | 2026-04-28 02:01:19 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-04 |
| 484 | 2026-04-28 02:01:20 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-04 |
| 485 | 2026-04-28 02:01:21 | system | N. Iyer | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q2 |
| 486 | 2026-04-28 02:01:22 | system | N. Iyer | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q2 |
| 487 | 2026-04-28 02:01:23 | system | N. Iyer | check_instance_created | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q2 |
| 488 | 2026-04-28 02:01:24 | system | N. Iyer | notification_logged | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q2 |
| 489 | 2026-04-28 02:01:25 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-04 |
| 490 | 2026-04-28 02:01:26 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-04 |
| 491 | 2026-04-28 02:01:27 | system | S. Haugen | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 492 | 2026-04-28 02:01:28 | system | S. Haugen | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 493 | 2026-04-28 02:01:29 | system | S. Haugen | check_instance_created | CheckInstance:CHK-TRAINING-PROC-2026-Q2 |
| 494 | 2026-04-28 02:01:30 | system | S. Haugen | notification_logged | CheckInstance:CHK-TRAINING-PROC-2026-Q2 |
| 495 | 2026-04-28 02:01:31 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1 |
| 496 | 2026-04-28 02:01:32 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 497 | 2026-04-28 02:01:33 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q1 |
| 498 | 2026-04-28 02:01:34 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 499 | 2026-04-28 02:01:35 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 500 | 2026-04-28 02:01:36 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q1 |
| 501 | 2026-04-28 02:01:37 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q1 |
| 502 | 2026-04-28 02:01:38 | system | L. Okafor | check_instance_overdue | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 503 | 2026-04-28 02:01:39 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 504 | 2026-04-28 02:01:40 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-03 |
| 505 | 2026-04-28 02:01:41 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-03 |
| 506 | 2026-04-28 02:01:42 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-03 |
| 507 | 2026-04-28 02:01:43 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-03 |
| 508 | 2026-04-28 02:01:44 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-03 |
| 509 | 2026-04-28 02:01:45 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-03 |
| 510 | 2026-04-28 02:01:46 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-HR-2026-03 |
| 511 | 2026-04-28 02:01:47 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-03 |
| 512 | 2026-04-28 02:01:48 | system | L. Okafor | check_instance_overdue | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 513 | 2026-04-28 02:01:49 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 514 | 2026-04-28 02:01:50 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-03 |
| 515 | 2026-04-28 02:01:51 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-03 |
| 516 | 2026-04-28 02:01:52 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q1 |
| 517 | 2026-04-28 02:01:53 | system | D. Ferreira | check_instance_overdue | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 518 | 2026-04-28 02:01:54 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 519 | 2026-04-28 02:01:55 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q1 |
| 520 | 2026-04-28 02:01:56 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 521 | 2026-04-28 02:01:57 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-03 |
| 522 | 2026-04-28 02:01:58 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-03 |
| 523 | 2026-04-28 02:01:59 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q1 |
| 524 | 2026-04-28 02:02:00 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q1 |
| 525 | 2026-04-28 02:02:01 | system | L. Okafor | check_instance_overdue | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 526 | 2026-04-28 02:02:02 | system | L. Okafor | notification_logged | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 527 | 2026-04-28 02:02:03 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-03 |
| 528 | 2026-04-28 02:02:04 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-03 |
| 529 | 2026-04-28 02:02:05 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-03 |
| 530 | 2026-04-28 02:02:06 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-03 |
| 531 | 2026-04-28 02:02:07 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q1 |
| 532 | 2026-04-28 02:02:08 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 533 | 2026-04-28 02:02:09 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1 |
| 534 | 2026-04-28 02:02:10 | system | N. Iyer | check_instance_overdue | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 535 | 2026-04-28 02:02:11 | system | N. Iyer | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 536 | 2026-04-28 02:02:12 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 537 | 2026-04-28 02:02:13 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q1 |
| 538 | 2026-04-28 02:02:14 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-TRAINING-FINREP-2026-Q1 |
| 539 | 2026-04-28 02:02:15 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-TRAINING-HR-2026-Q1 |
| 540 | 2026-04-28 02:02:16 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q1 |
| 541 | 2026-04-28 02:02:17 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q1 |
| 542 | 2026-04-28 02:02:18 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-TRAINING-PROC-2026-Q1 |
| 543 | 2026-04-28 02:02:19 | user | user | cycle_completed | Cycle:2026-04-28 |
| 544 | 2026-04-28 03:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0031 |
| 545 | 2026-04-28 03:00:01 | system | R. Mehta | finding_recorded | Finding:FND-BACKUP-VERIFY-CUSTOPS-2026-03-1 |
| 546 | 2026-04-28 03:00:02 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0041 |
| 547 | 2026-04-28 03:00:03 | system | A. Novak | finding_recorded | Finding:FND-BACKUP-VERIFY-FINREP-2026-03-1 |
| 548 | 2026-04-28 03:00:04 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0050 |
| 549 | 2026-04-28 03:00:05 | system | L. Okafor | finding_recorded | Finding:FND-BACKUP-VERIFY-PAYMENTS-2026-03-1 |
| 550 | 2026-04-28 03:00:06 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0061 |
| 551 | 2026-04-28 03:00:07 | system | N. Iyer | finding_recorded | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-03-1 |
| 552 | 2026-04-28 03:00:08 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0075 |
| 553 | 2026-04-28 03:00:09 | system | R. Mehta | finding_recorded | Finding:FND-CHANGE-MGMT-CUSTOPS-2026-03-1 |
| 554 | 2026-04-28 03:00:10 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0086 |
| 555 | 2026-04-28 03:00:11 | system | A. Novak | finding_recorded | Finding:FND-CHANGE-MGMT-FINREP-2026-03-1 |
| 556 | 2026-04-28 03:00:12 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0096 |
| 557 | 2026-04-28 03:00:13 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0106 |
| 558 | 2026-04-28 03:00:14 | system | L. Okafor | finding_recorded | Finding:FND-CHANGE-MGMT-PAYMENTS-2026-03-1 |
| 559 | 2026-04-28 03:00:15 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0128 |
| 560 | 2026-04-28 03:00:16 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0139 |
| 561 | 2026-04-28 03:00:17 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0163 |
| 562 | 2026-04-28 03:00:18 | system | R. Mehta | finding_recorded | Finding:FND-CUST-COMPLAINTS-CUSTOPS-2026-03-1 |
| 563 | 2026-04-28 03:00:19 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0174 |
| 564 | 2026-04-28 03:00:20 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0186 |
| 565 | 2026-04-28 03:00:21 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0216 |
| 566 | 2026-04-28 03:00:22 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0227 |
| 567 | 2026-04-28 03:00:23 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0239 |
| 568 | 2026-04-28 03:00:24 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0250 |
| 569 | 2026-04-28 03:00:25 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0001 |
| 570 | 2026-04-28 03:00:26 | system | R. Mehta | finding_recorded | Finding:FND-ACCESS-EXPORT-CUSTOPS-2026-Q1-1 |
| 571 | 2026-04-28 03:00:27 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0005 |
| 572 | 2026-04-28 03:00:28 | system | D. Ferreira | finding_recorded | Finding:FND-ACCESS-EXPORT-HR-2026-Q1-1 |
| 573 | 2026-04-28 03:00:29 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0008 |
| 574 | 2026-04-28 03:00:30 | system | J. Alvarez | finding_recorded | Finding:FND-ACCESS-EXPORT-MKTG-2026-Q1-1 |
| 575 | 2026-04-28 03:00:31 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0012 |
| 576 | 2026-04-28 03:00:32 | system | L. Okafor | finding_recorded | Finding:FND-ACCESS-EXPORT-PAYMENTS-2026-Q1-1 |
| 577 | 2026-04-28 03:00:33 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0016 |
| 578 | 2026-04-28 03:00:34 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0019 |
| 579 | 2026-04-28 03:00:35 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0023 |
| 580 | 2026-04-28 03:00:36 | system | L. Okafor | finding_recorded | Finding:FND-ACCESS-REVIEW-PAYMENTS-2026-Q1-1 |
| 581 | 2026-04-28 03:00:37 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0147 |
| 582 | 2026-04-28 03:00:38 | system | D. Ferreira | finding_recorded | Finding:FND-CRYPTO-KEY-HR-2026-Q1-1 |
| 583 | 2026-04-28 03:00:39 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0154 |
| 584 | 2026-04-28 03:00:40 | system | J. Alvarez | finding_recorded | Finding:FND-CRYPTO-KEY-MKTG-2026-Q1-1 |
| 585 | 2026-04-28 03:00:41 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0200 |
| 586 | 2026-04-28 03:00:42 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0204 |
| 587 | 2026-04-28 03:00:43 | system | L. Okafor | finding_recorded | Finding:FND-DATA-RETENTION-PAYMENTS-2026-Q1-1 |
| 588 | 2026-04-28 03:00:44 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0264 |
| 589 | 2026-04-28 03:00:45 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0270 |
| 590 | 2026-04-28 03:00:46 | system | N. Iyer | finding_recorded | Finding:FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1 |
| 591 | 2026-04-28 03:00:47 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0280 |
| 592 | 2026-04-28 03:00:48 | system | R. Mehta | finding_recorded | Finding:FND-TRAINING-CUSTOPS-2026-Q1-1 |
| 593 | 2026-04-28 03:00:49 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0284 |
| 594 | 2026-04-28 03:00:50 | system | A. Novak | finding_recorded | Finding:FND-TRAINING-FINREP-2026-Q1-1 |
| 595 | 2026-04-28 03:00:51 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0287 |
| 596 | 2026-04-28 03:00:52 | system | D. Ferreira | finding_recorded | Finding:FND-TRAINING-HR-2026-Q1-1 |
| 597 | 2026-04-28 03:00:53 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0295 |
| 598 | 2026-04-28 03:00:54 | system | L. Okafor | finding_recorded | Finding:FND-TRAINING-PAYMENTS-2026-Q1-1 |
| 599 | 2026-04-28 03:00:55 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0299 |
| 600 | 2026-04-28 03:00:56 | system | N. Iyer | finding_recorded | Finding:FND-TRAINING-PLATFORM-2026-Q1-1 |
| 601 | 2026-04-28 03:00:57 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0303 |
| 602 | 2026-04-28 03:00:58 | system | S. Haugen | finding_recorded | Finding:FND-TRAINING-PROC-2026-Q1-1 |
| 603 | 2026-04-28 03:00:59 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0265 |
| 604 | 2026-04-28 03:01:00 | system | D. Ferreira | finding_recorded | Finding:FND-THIRD-PARTY-ACCESS-HR-2026-Q2-1 |
| 605 | 2026-04-28 03:01:01 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0277 |
| 606 | 2026-04-28 03:01:02 | system | S. Haugen | finding_recorded | Finding:FND-THIRD-PARTY-ACCESS-PROC-2026-Q2-1 |
| 607 | 2026-04-28 03:01:03 | system | prescreen | prescreen_completed | Cycle:2026-04-28 |
| 608 | 2026-04-28 04:00:00 | ai | D. Ferreira | finding_recorded | Finding:FND-CHANGE-MGMT-HR-2026-03-1 |
| 609 | 2026-04-28 04:00:01 | ai | J. Alvarez | finding_recorded | Finding:FND-CHANGE-MGMT-MKTG-2026-03-1 |
| 610 | 2026-04-28 04:00:02 | ai | N. Iyer | finding_recorded | Finding:FND-CHANGE-MGMT-PLATFORM-2026-03-1 |
| 611 | 2026-04-28 04:00:03 | ai | S. Haugen | finding_recorded | Finding:FND-CHANGE-MGMT-PROC-2026-03-1 |
| 612 | 2026-04-28 04:00:04 | ai | J. Alvarez | finding_recorded | Finding:FND-CUST-COMPLAINTS-MKTG-2026-03-1 |
| 613 | 2026-04-28 04:00:05 | ai | L. Okafor | finding_recorded | Finding:FND-CUST-COMPLAINTS-PAYMENTS-2026-03-1 |
| 614 | 2026-04-28 04:00:06 | ai | R. Mehta | finding_recorded | Finding:FND-INCIDENT-PM-CUSTOPS-2026-03-1 |
| 615 | 2026-04-28 04:00:07 | ai | A. Novak | finding_recorded | Finding:FND-INCIDENT-PM-FINREP-2026-03-1 |
| 616 | 2026-04-28 04:00:08 | ai | L. Okafor | finding_recorded | Finding:FND-INCIDENT-PM-PAYMENTS-2026-03-1 |
| 617 | 2026-04-28 04:00:09 | ai | N. Iyer | finding_recorded | Finding:FND-INCIDENT-PM-PLATFORM-2026-03-1 |
| 618 | 2026-04-28 04:00:10 | ai | R. Mehta | finding_recorded | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 619 | 2026-04-28 04:00:11 | ai | D. Ferreira | finding_recorded | Finding:FND-ACCESS-REVIEW-HR-2026-Q1-1 |
| 620 | 2026-04-28 04:00:12 | ai | J. Alvarez | finding_recorded | Finding:FND-ACCESS-REVIEW-MKTG-2026-Q1-1 |
| 621 | 2026-04-28 04:00:13 | ai | R. Mehta | finding_recorded | Finding:FND-CRYPTO-KEY-CUSTOPS-2026-Q1-1 |
| 622 | 2026-04-28 04:00:14 | ai | D. Ferreira | finding_recorded | Finding:FND-DATA-RETENTION-HR-2026-Q1-1 |
| 623 | 2026-04-28 04:00:15 | ai | J. Alvarez | finding_recorded | Finding:FND-DATA-RETENTION-MKTG-2026-Q1-1 |
| 624 | 2026-04-28 04:00:16 | ai | D. Ferreira | finding_recorded | Finding:FND-THIRD-PARTY-ACCESS-HR-2026-Q1-1 |
| 625 | 2026-04-28 04:00:17 | ai | L. Okafor | finding_recorded | Finding:FND-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1-1 |
| 626 | 2026-04-28 04:00:18 | system | assessor | assessment_completed | Cycle:2026-04-28 |
| 627 | 2026-04-28 05:00:00 | system | L. Okafor | flag_raised | Flag:FLG-GAP-FND-ACCESS-EXPORT-PAYMENTS-2026-Q1-1 |
| 628 | 2026-04-28 05:00:01 | system | L. Okafor | action_raised | Action:ACT-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 629 | 2026-04-28 05:00:02 | system | L. Okafor | action_assigned | Action:ACT-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 630 | 2026-04-28 05:00:03 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 631 | 2026-04-28 05:00:04 | system | R. Mehta | action_raised | Action:ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 632 | 2026-04-28 05:00:05 | system | R. Mehta | action_assigned | Action:ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 633 | 2026-04-28 05:00:06 | system | D. Ferreira | flag_raised | Flag:FLG-GAP-FND-ACCESS-REVIEW-HR-2026-Q1-1 |
| 634 | 2026-04-28 05:00:07 | system | D. Ferreira | action_raised | Action:ACT-ACCESS-REVIEW-HR-2026-Q1 |
| 635 | 2026-04-28 05:00:08 | system | D. Ferreira | action_assigned | Action:ACT-ACCESS-REVIEW-HR-2026-Q1 |
| 636 | 2026-04-28 05:00:09 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-FND-ACCESS-REVIEW-MKTG-2026-Q1-1 |
| 637 | 2026-04-28 05:00:10 | system | J. Alvarez | action_raised | Action:ACT-ACCESS-REVIEW-MKTG-2026-Q1 |
| 638 | 2026-04-28 05:00:11 | system | J. Alvarez | action_assigned | Action:ACT-ACCESS-REVIEW-MKTG-2026-Q1 |
| 639 | 2026-04-28 05:00:12 | system | L. Okafor | flag_raised | Flag:FLG-OVERDUE-FND-ACCESS-REVIEW-PAYMENTS-2026-Q1-1 |
| 640 | 2026-04-28 05:00:13 | system | L. Okafor | action_raised | Action:ACT-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 641 | 2026-04-28 05:00:14 | system | L. Okafor | action_assigned | Action:ACT-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 642 | 2026-04-28 05:00:15 | system | N. Iyer | flag_raised | Flag:FLG-GAP-FND-BACKUP-VERIFY-PLATFORM-2026-03-1 |
| 643 | 2026-04-28 05:00:16 | system | N. Iyer | action_raised | Action:ACT-BACKUP-VERIFY-PLATFORM-2026-03 |
| 644 | 2026-04-28 05:00:17 | system | N. Iyer | action_assigned | Action:ACT-BACKUP-VERIFY-PLATFORM-2026-03 |
| 645 | 2026-04-28 05:00:18 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-CHANGE-MGMT-CUSTOPS-2026-03-1 |
| 646 | 2026-04-28 05:00:19 | system | R. Mehta | action_raised | Action:ACT-CHANGE-MGMT-CUSTOPS-2026-03 |
| 647 | 2026-04-28 05:00:20 | system | R. Mehta | action_assigned | Action:ACT-CHANGE-MGMT-CUSTOPS-2026-03 |
| 648 | 2026-04-28 05:00:21 | system | A. Novak | flag_raised | Flag:FLG-GAP-FND-CHANGE-MGMT-FINREP-2026-03-1 |
| 649 | 2026-04-28 05:00:22 | system | A. Novak | action_raised | Action:ACT-CHANGE-MGMT-FINREP-2026-03 |
| 650 | 2026-04-28 05:00:23 | system | A. Novak | action_assigned | Action:ACT-CHANGE-MGMT-FINREP-2026-03 |
| 651 | 2026-04-28 05:00:24 | system | D. Ferreira | flag_raised | Flag:FLG-GAP-FND-CHANGE-MGMT-HR-2026-03-1 |
| 652 | 2026-04-28 05:00:25 | system | D. Ferreira | action_raised | Action:ACT-CHANGE-MGMT-HR-2026-03 |
| 653 | 2026-04-28 05:00:26 | system | D. Ferreira | action_assigned | Action:ACT-CHANGE-MGMT-HR-2026-03 |
| 654 | 2026-04-28 05:00:27 | system | L. Okafor | flag_raised | Flag:FLG-OVERDUE-FND-CHANGE-MGMT-PAYMENTS-2026-03-1 |
| 655 | 2026-04-28 05:00:28 | system | L. Okafor | action_raised | Action:ACT-CHANGE-MGMT-PAYMENTS-2026-03 |
| 656 | 2026-04-28 05:00:29 | system | L. Okafor | action_assigned | Action:ACT-CHANGE-MGMT-PAYMENTS-2026-03 |
| 657 | 2026-04-28 05:00:30 | system | N. Iyer | flag_raised | Flag:FLG-GAP-FND-CHANGE-MGMT-PLATFORM-2026-03-1 |
| 658 | 2026-04-28 05:00:31 | system | N. Iyer | action_raised | Action:ACT-CHANGE-MGMT-PLATFORM-2026-03 |
| 659 | 2026-04-28 05:00:32 | system | N. Iyer | action_assigned | Action:ACT-CHANGE-MGMT-PLATFORM-2026-03 |
| 660 | 2026-04-28 05:00:33 | system | D. Ferreira | flag_raised | Flag:FLG-OVERDUE-FND-CRYPTO-KEY-HR-2026-Q1-1 |
| 661 | 2026-04-28 05:00:34 | system | D. Ferreira | action_raised | Action:ACT-CRYPTO-KEY-HR-2026-Q1 |
| 662 | 2026-04-28 05:00:35 | system | D. Ferreira | action_assigned | Action:ACT-CRYPTO-KEY-HR-2026-Q1 |
| 663 | 2026-04-28 05:00:36 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-FND-CRYPTO-KEY-MKTG-2026-Q1-1 |
| 664 | 2026-04-28 05:00:37 | system | J. Alvarez | action_raised | Action:ACT-CRYPTO-KEY-MKTG-2026-Q1 |
| 665 | 2026-04-28 05:00:38 | system | J. Alvarez | action_assigned | Action:ACT-CRYPTO-KEY-MKTG-2026-Q1 |
| 666 | 2026-04-28 05:00:39 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-CUST-COMPLAINTS-CUSTOPS-2026-03-1 |
| 667 | 2026-04-28 05:00:40 | system | R. Mehta | action_raised | Action:ACT-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 668 | 2026-04-28 05:00:41 | system | R. Mehta | action_assigned | Action:ACT-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 669 | 2026-04-28 05:00:42 | system | D. Ferreira | flag_raised | Flag:FLG-GAP-FND-DATA-RETENTION-HR-2026-Q1-1 |
| 670 | 2026-04-28 05:00:43 | system | D. Ferreira | action_raised | Action:ACT-DATA-RETENTION-HR-2026-Q1 |
| 671 | 2026-04-28 05:00:44 | system | D. Ferreira | action_assigned | Action:ACT-DATA-RETENTION-HR-2026-Q1 |
| 672 | 2026-04-28 05:00:45 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-FND-DATA-RETENTION-MKTG-2026-Q1-1 |
| 673 | 2026-04-28 05:00:46 | system | J. Alvarez | action_raised | Action:ACT-DATA-RETENTION-MKTG-2026-Q1 |
| 674 | 2026-04-28 05:00:47 | system | J. Alvarez | action_assigned | Action:ACT-DATA-RETENTION-MKTG-2026-Q1 |
| 675 | 2026-04-28 05:00:48 | system | L. Okafor | flag_raised | Flag:FLG-OVERDUE-FND-DATA-RETENTION-PAYMENTS-2026-Q1-1 |
| 676 | 2026-04-28 05:00:49 | system | L. Okafor | action_raised | Action:ACT-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 677 | 2026-04-28 05:00:50 | system | L. Okafor | action_assigned | Action:ACT-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 678 | 2026-04-28 05:00:51 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-CUSTOPS-2026-03-1 |
| 679 | 2026-04-28 05:00:52 | system | R. Mehta | action_raised | Action:ACT-INCIDENT-PM-CUSTOPS-2026-03 |
| 680 | 2026-04-28 05:00:53 | system | R. Mehta | action_assigned | Action:ACT-INCIDENT-PM-CUSTOPS-2026-03 |
| 681 | 2026-04-28 05:00:54 | system | A. Novak | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-FINREP-2026-03-1 |
| 682 | 2026-04-28 05:00:55 | system | A. Novak | action_raised | Action:ACT-INCIDENT-PM-FINREP-2026-03 |
| 683 | 2026-04-28 05:00:56 | system | A. Novak | action_assigned | Action:ACT-INCIDENT-PM-FINREP-2026-03 |
| 684 | 2026-04-28 05:00:57 | system | N. Iyer | flag_raised | Flag:FLG-GAP-FND-INCIDENT-PM-PLATFORM-2026-03-1 |
| 685 | 2026-04-28 05:00:58 | system | N. Iyer | action_raised | Action:ACT-INCIDENT-PM-PLATFORM-2026-03 |
| 686 | 2026-04-28 05:00:59 | system | N. Iyer | action_assigned | Action:ACT-INCIDENT-PM-PLATFORM-2026-03 |
| 687 | 2026-04-28 05:01:00 | system | D. Ferreira | flag_raised | Flag:FLG-GAP-FND-THIRD-PARTY-ACCESS-HR-2026-Q2-1 |
| 688 | 2026-04-28 05:01:01 | system | D. Ferreira | action_raised | Action:ACT-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 689 | 2026-04-28 05:01:02 | system | D. Ferreira | action_assigned | Action:ACT-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 690 | 2026-04-28 05:01:03 | system | N. Iyer | flag_raised | Flag:FLG-OVERDUE-FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1 |
| 691 | 2026-04-28 05:01:04 | system | N. Iyer | action_raised | Action:ACT-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 692 | 2026-04-28 05:01:05 | system | N. Iyer | action_assigned | Action:ACT-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 693 | 2026-04-28 05:01:06 | system | S. Haugen | flag_raised | Flag:FLG-GAP-FND-THIRD-PARTY-ACCESS-PROC-2026-Q2-1 |
| 694 | 2026-04-28 05:01:07 | system | S. Haugen | action_raised | Action:ACT-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 695 | 2026-04-28 05:01:08 | system | S. Haugen | action_assigned | Action:ACT-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 696 | 2026-04-28 05:01:09 | system | R. Mehta | flag_raised | Flag:FLG-GAP-FND-TRAINING-CUSTOPS-2026-Q1-1 |
| 697 | 2026-04-28 05:01:10 | system | R. Mehta | action_raised | Action:ACT-TRAINING-CUSTOPS-2026-Q1 |
| 698 | 2026-04-28 05:01:11 | system | R. Mehta | action_assigned | Action:ACT-TRAINING-CUSTOPS-2026-Q1 |
| 699 | 2026-04-28 05:01:12 | system | N. Iyer | flag_raised | Flag:FLG-GAP-FND-TRAINING-PLATFORM-2026-Q1-1 |
| 700 | 2026-04-28 05:01:13 | system | N. Iyer | action_raised | Action:ACT-TRAINING-PLATFORM-2026-Q1 |
| 701 | 2026-04-28 05:01:14 | system | N. Iyer | action_assigned | Action:ACT-TRAINING-PLATFORM-2026-Q1 |
| 702 | 2026-04-28 05:01:15 | system | S. Haugen | flag_raised | Flag:FLG-GAP-FND-TRAINING-PROC-2026-Q1-1 |
| 703 | 2026-04-28 05:01:16 | system | S. Haugen | action_raised | Action:ACT-TRAINING-PROC-2026-Q1 |
| 704 | 2026-04-28 05:01:17 | system | S. Haugen | action_assigned | Action:ACT-TRAINING-PROC-2026-Q1 |
| 705 | 2026-04-28 05:01:18 | system | Group Compliance | action_escalated | Action:ACT-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 706 | 2026-04-28 05:01:19 | system | Group Compliance | action_escalated | Action:ACT-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 707 | 2026-04-28 05:01:20 | system | Group Compliance | action_escalated | Action:ACT-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 708 | 2026-04-28 05:01:21 | system | Group Compliance | action_escalated | Action:ACT-CHANGE-MGMT-PAYMENTS-2026-02 |
| 709 | 2026-04-28 05:01:22 | system | Group Compliance | action_escalated | Action:ACT-CHANGE-MGMT-PLATFORM-2026-01 |
| 710 | 2026-04-28 05:01:23 | system | Group Compliance | action_escalated | Action:ACT-CUST-COMPLAINTS-MKTG-2026-01 |
| 711 | 2026-04-28 05:01:24 | system | Group Compliance | action_escalated | Action:ACT-DPIA-MKTG-2026 |
| 712 | 2026-04-28 05:01:25 | system | Group Compliance | action_escalated | Action:ACT-INCIDENT-PM-PAYMENTS-2026-02 |
| 713 | 2026-04-28 05:01:26 | system | Group Compliance | action_escalated | Action:ACT-INCIDENT-PM-PLATFORM-2026-01 |
| 714 | 2026-04-28 05:01:27 | system | Group Compliance | action_escalated | Action:ACT-TRAINING-MKTG-2026-Q1 |
| 715 | 2026-04-28 05:01:28 | system | flagging | flagging_completed | Cycle:2026-04-28 |
| 716 | 2026-04-28 09:30:00 | user | R. Mehta | evidence_uploaded | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 717 | 2026-04-28 06:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-UI-0317 |
| 718 | 2026-04-28 06:00:01 | user | R. Mehta | remediation_submitted | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 719 | 2026-04-28 06:00:02 | user | R. Mehta | action_in_progress | Action:ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 720 | 2026-04-28 06:00:03 | user | R. Mehta | action_remediation_submitted | Action:ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 721 | 2026-04-28 06:00:04 | ai | R. Mehta | finding_recorded | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-2 |
| 722 | 2026-04-28 06:00:05 | system | R. Mehta | finding_superseded | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 723 | 2026-04-28 06:00:06 | system | R. Mehta | action_reassessed | Action:ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 724 | 2026-04-28 06:00:07 | system | R. Mehta | action_resolved | Action:ACT-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 725 | 2026-04-28 06:00:08 | system | R. Mehta | flag_closed | Flag:FLG-GAP-FND-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
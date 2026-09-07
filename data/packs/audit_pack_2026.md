# Audit Evidence Pack — Northwind Group (fictional)

**Period covered** 2026-01-01 to 2026-12-31  
**Scope** All auditable units, all applicable controls  
**Generated** 2026-09-08 01:30:01  
**Source** append-only audit log, 1,255 events  
**Chain integrity** VERIFIED — 1,255 entries, chain intact

| | |
|---|---|
| Auditable units | 11 |
| Controls exercised | 14 |
| Checks due | 224 |
| Checks completed | 129 |
| Checks waived | 0 |
| Checks not examined | 95 |
| Findings recorded | 145 |
| Findings superseded by re-assessment | 16 |
| Current non-compliant findings | 9 |
| Flagged for human review | 0 |
| Decided without a model call | 41 |
| Exceptions on register | 4 |
| Findings raised | 35 |
| Findings closed | 21 |

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
| People Operations | Third-party access recertification | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| People Operations | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
| IT Services | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| IT Services | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| IT Services | Backup restore verification | monthly | 4 | 3 | 0 | 1 |
| IT Services | Business continuity plan test | annual | 1 | 0 | 0 | 1 |
| IT Services | Change management approval | monthly | 4 | 3 | 0 | 1 |
| IT Services | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| IT Services | Data retention schedule adherence | quarterly | 2 | 2 | 0 | 0 |
| IT Services | Data protection impact assessment currency | annual | 1 | 0 | 0 | 1 |
| IT Services | Incident post-mortem completion | monthly | 4 | 3 | 0 | 1 |
| IT Services | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| IT Services | Third-party access recertification | quarterly | 2 | 1 | 0 | 1 |
| IT Services | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| IT Services | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
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
| Project Atlas | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| Project Atlas | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| Project Atlas | Backup restore verification | monthly | 4 | 3 | 0 | 1 |
| Project Atlas | Business continuity plan test | annual | 1 | 0 | 0 | 1 |
| Project Atlas | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Project Atlas | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| Project Atlas | Customer complaint handling SLA | monthly | 4 | 3 | 0 | 1 |
| Project Atlas | Data retention schedule adherence | quarterly | 2 | 1 | 0 | 1 |
| Project Atlas | Data protection impact assessment currency | annual | 1 | 0 | 0 | 1 |
| Project Atlas | Incident post-mortem completion | monthly | 4 | 4 | 0 | 0 |
| Project Atlas | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Project Beacon | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Project Beacon | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| Project Beacon | Third-party access recertification | quarterly | 2 | 1 | 0 | 1 |
| Project Beacon | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Project Beacon | Annual vendor due diligence | annual | 1 | 0 | 0 | 1 |
| Project Coral | Access review export completeness | quarterly | 2 | 1 | 0 | 1 |
| Project Coral | Quarterly privileged access review | quarterly | 2 | 1 | 0 | 1 |
| Project Coral | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Project Coral | Encryption key rotation | quarterly | 2 | 1 | 0 | 1 |
| Project Coral | Data retention schedule adherence | quarterly | 2 | 1 | 0 | 1 |
| Project Coral | Data protection impact assessment currency | annual | 1 | 0 | 0 | 1 |
| Project Coral | Mandatory compliance training completion | quarterly | 2 | 1 | 0 | 1 |
| Procurement | Change management approval | monthly | 4 | 3 | 0 | 1 |
| Procurement | Supplier security attestation | annual | 1 | 0 | 0 | 1 |
| Procurement | Third-party access recertification | quarterly | 2 | 1 | 0 | 1 |
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

### ASM-ACCESS-EXPORT-CUSTOPS-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### ASM-ACCESS-EXPORT-HR-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-HR-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** No evidence was submitted for 2026-Q1 against Access review export completeness. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### ASM-ACCESS-EXPORT-ITSVC-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-ITSVC-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### ASM-ACCESS-EXPORT-MKTG-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-MKTG-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### ASM-ACCESS-EXPORT-PAYMENTS-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** No evidence was submitted for 2026-Q1 against Access review export completeness. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### ASM-ACCESS-EXPORT-PRJ-ATLAS-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-PRJ-ATLAS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### ASM-ACCESS-EXPORT-PRJ-CORAL-2026-Q1-1

- **Check** CHK-ACCESS-EXPORT-PRJ-CORAL-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by M. Dubois
- **Rationale** All thresholds met: dormant_unresolved was 0 against a required at most 0; reviewed_pct was 100.0 against a required at least 100.0.
- **Cited evidence** > "dormant_unresolved": 0
- **Cited evidence** > "reviewed_pct": 100.0

### ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 *(superseded by ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-2)*

- **Check** CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 3. 4 dormant accounts were identified but revocation is still pending and no justification has been recorded for them.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `b35929f49bab`

### ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-2

- **Check** CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - Customer Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `b2498f3dc5c6`

### ASM-ACCESS-REVIEW-HR-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-HR-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - People Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `75745e0e54da`

### ASM-ACCESS-REVIEW-ITSVC-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-ITSVC-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - IT Services - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `f7e879fe7d64`

### ASM-ACCESS-REVIEW-MKTG-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-MKTG-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - Marketing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `3a175bbe6ddd`

### ASM-ACCESS-REVIEW-PAYMENTS-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - Payments Processing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `b98f10f7d92f`

### ASM-ACCESS-REVIEW-PRJ-ATLAS-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-PRJ-ATLAS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - Project Atlas - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `f4740a9061c4`

### ASM-ACCESS-REVIEW-PRJ-CORAL-2026-Q1-1

- **Check** CHK-ACCESS-REVIEW-PRJ-CORAL-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by M. Dubois
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Quarterly privileged access review - Project Coral - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `c5d1654c78801aa2` · evidence `15a842ba70db`

### ASM-BACKUP-VERIFY-CUSTOPS-2026-01-1

- **Check** CHK-BACKUP-VERIFY-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** All thresholds met: max_rto_minutes was 46 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 46
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-CUSTOPS-2026-02-1

- **Check** CHK-BACKUP-VERIFY-CUSTOPS-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** All thresholds met: max_rto_minutes was 42 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 42
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-CUSTOPS-2026-03-1

- **Check** CHK-BACKUP-VERIFY-CUSTOPS-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** All thresholds met: max_rto_minutes was 34 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 34
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-FINREP-2026-01-1

- **Check** CHK-BACKUP-VERIFY-FINREP-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by A. Novak
- **Rationale** All thresholds met: max_rto_minutes was 48 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 48
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-FINREP-2026-02-1

- **Check** CHK-BACKUP-VERIFY-FINREP-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** All thresholds met: max_rto_minutes was 20 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 20
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-FINREP-2026-03-1

- **Check** CHK-BACKUP-VERIFY-FINREP-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** All thresholds met: max_rto_minutes was 34 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 34
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-ITSVC-2026-01-1

- **Check** CHK-BACKUP-VERIFY-ITSVC-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by C. Brennan
- **Rationale** All thresholds met: max_rto_minutes was 37 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 37
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-ITSVC-2026-02-1

- **Check** CHK-BACKUP-VERIFY-ITSVC-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by C. Brennan
- **Rationale** All thresholds met: max_rto_minutes was 36 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 36
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-ITSVC-2026-03-1

- **Check** CHK-BACKUP-VERIFY-ITSVC-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** All thresholds met: max_rto_minutes was 46 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 46
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PAYMENTS-2026-01-1

- **Check** CHK-BACKUP-VERIFY-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** All thresholds met: max_rto_minutes was 27 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 27
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PAYMENTS-2026-02-1

- **Check** CHK-BACKUP-VERIFY-PAYMENTS-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** All thresholds met: max_rto_minutes was 29 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 29
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PAYMENTS-2026-03-1

- **Check** CHK-BACKUP-VERIFY-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** All thresholds met: max_rto_minutes was 55 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 55
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PLATFORM-2026-01-1

- **Check** CHK-BACKUP-VERIFY-PLATFORM-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by N. Iyer
- **Rationale** All thresholds met: max_rto_minutes was 49 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 49
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PLATFORM-2026-02-1

- **Check** CHK-BACKUP-VERIFY-PLATFORM-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** All thresholds met: max_rto_minutes was 23 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 23
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PLATFORM-2026-03-1

- **Check** CHK-BACKUP-VERIFY-PLATFORM-2026-03  
- **Verdict** `gap` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** Threshold evaluation failed: max_rto_minutes was 39 against a required at most 60; success_pct was 93.6 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 39
- **Cited evidence** > "success_pct": 93.6
- **Gap** success_pct was 93.6, outside the required at least 95.0.

### ASM-BACKUP-VERIFY-PRJ-ATLAS-2026-01-1

- **Check** CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-01  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-02-27 by E. Vasquez
- **Rationale** All thresholds met: max_rto_minutes was 51 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 51
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PRJ-ATLAS-2026-02-1

- **Check** CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-02  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-03-29 by E. Vasquez
- **Rationale** All thresholds met: max_rto_minutes was 26 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 26
- **Cited evidence** > "success_pct": 100.0

### ASM-BACKUP-VERIFY-PRJ-ATLAS-2026-03-1

- **Check** CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-03  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** All thresholds met: max_rto_minutes was 41 against a required at most 60; success_pct was 100.0 against a required at least 95.0.
- **Cited evidence** > "max_rto_minutes": 41
- **Cited evidence** > "success_pct": 100.0

### ASM-CHANGE-MGMT-CUSTOPS-2026-01-1

- **Check** CHK-CHANGE-MGMT-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Customer Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `f6e0320defbc`

### ASM-CHANGE-MGMT-CUSTOPS-2026-02-1

- **Check** CHK-CHANGE-MGMT-CUSTOPS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Customer Operations - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `6756cc313c31`

### ASM-CHANGE-MGMT-CUSTOPS-2026-03-1

- **Check** CHK-CHANGE-MGMT-CUSTOPS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Customer Operations - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `0041c2304c68`

### ASM-CHANGE-MGMT-FINREP-2026-01-1

- **Check** CHK-CHANGE-MGMT-FINREP-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Financial Reporting - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `0e6d3e1f0eec`

### ASM-CHANGE-MGMT-FINREP-2026-02-1 *(superseded by ASM-CHANGE-MGMT-FINREP-2026-02-2)*

- **Check** CHK-CHANGE-MGMT-FINREP-2026-02  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 3. No reconciliation against the deployment log was performed.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `b417c1900f6a`

### ASM-CHANGE-MGMT-FINREP-2026-02-2

- **Check** CHK-CHANGE-MGMT-FINREP-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Financial Reporting - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `778a4cf7b9bd`

### ASM-CHANGE-MGMT-FINREP-2026-03-1

- **Check** CHK-CHANGE-MGMT-FINREP-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Financial Reporting - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `f438ba240f81`

### ASM-CHANGE-MGMT-HR-2026-01-1

- **Check** CHK-CHANGE-MGMT-HR-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - People Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `e9511a562f90`

### ASM-CHANGE-MGMT-HR-2026-02-1

- **Check** CHK-CHANGE-MGMT-HR-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - People Operations - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `86f48f52190c`

### ASM-CHANGE-MGMT-HR-2026-03-1

- **Check** CHK-CHANGE-MGMT-HR-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - People Operations - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `dc5d6a439ce4`

### ASM-CHANGE-MGMT-ITSVC-2026-01-1

- **Check** CHK-CHANGE-MGMT-ITSVC-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - IT Services - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `d48d0d2201bb`

### ASM-CHANGE-MGMT-ITSVC-2026-02-1

- **Check** CHK-CHANGE-MGMT-ITSVC-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - IT Services - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `e9328a7663a0`

### ASM-CHANGE-MGMT-ITSVC-2026-03-1

- **Check** CHK-CHANGE-MGMT-ITSVC-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - IT Services - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `3d0e8125971d`

### ASM-CHANGE-MGMT-MKTG-2026-01-1

- **Check** CHK-CHANGE-MGMT-MKTG-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Marketing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `3b37515ee88f`

### ASM-CHANGE-MGMT-MKTG-2026-02-1 *(superseded by ASM-CHANGE-MGMT-MKTG-2026-02-2)*

- **Check** CHK-CHANGE-MGMT-MKTG-2026-02  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by J. Alvarez
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 1. Production changes were deployed with no approval records at all.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `5f7f0e0b35d1`

### ASM-CHANGE-MGMT-MKTG-2026-02-2

- **Check** CHK-CHANGE-MGMT-MKTG-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Marketing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `3228e4282f63`

### ASM-CHANGE-MGMT-MKTG-2026-03-1

- **Check** CHK-CHANGE-MGMT-MKTG-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Marketing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `b720c6723e5a`

### ASM-CHANGE-MGMT-PAYMENTS-2026-01-1 *(superseded by ASM-CHANGE-MGMT-PAYMENTS-2026-01-2)*

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Payments Processing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `e0de996fa55a`

### ASM-CHANGE-MGMT-PAYMENTS-2026-01-2

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Payments Processing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `07782357b53f`

### ASM-CHANGE-MGMT-PAYMENTS-2026-02-1

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Payments Processing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `868ede8dfb31`

### ASM-CHANGE-MGMT-PAYMENTS-2026-03-1

- **Check** CHK-CHANGE-MGMT-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Payments Processing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `fe5c4ce4ceb3`

### ASM-CHANGE-MGMT-PLATFORM-2026-01-1

- **Check** CHK-CHANGE-MGMT-PLATFORM-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Platform Engineering - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `9a05eb1552bf`

### ASM-CHANGE-MGMT-PLATFORM-2026-02-1

- **Check** CHK-CHANGE-MGMT-PLATFORM-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Platform Engineering - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `e75e6c5188b4`

### ASM-CHANGE-MGMT-PLATFORM-2026-03-1

- **Check** CHK-CHANGE-MGMT-PLATFORM-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Platform Engineering - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `f345fbbd7e21`

### ASM-CHANGE-MGMT-PRJ-ATLAS-2026-01-1

- **Check** CHK-CHANGE-MGMT-PRJ-ATLAS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Atlas - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `a0ffd5b21b17`

### ASM-CHANGE-MGMT-PRJ-ATLAS-2026-02-1

- **Check** CHK-CHANGE-MGMT-PRJ-ATLAS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Atlas - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `a628be5bb4de`

### ASM-CHANGE-MGMT-PRJ-ATLAS-2026-03-1

- **Check** CHK-CHANGE-MGMT-PRJ-ATLAS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Atlas - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `667148c7e955`

### ASM-CHANGE-MGMT-PRJ-BEACON-2026-01-1

- **Check** CHK-CHANGE-MGMT-PRJ-BEACON-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by K. Tanaka
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Beacon - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `04a03312fec2`

### ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1 *(superseded by ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-2)*

- **Check** CHK-CHANGE-MGMT-PRJ-BEACON-2026-02  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by K. Tanaka
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 2. 2 emergency changes were never reviewed.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `fe25b10b01a9`

### ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-2

- **Check** CHK-CHANGE-MGMT-PRJ-BEACON-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by K. Tanaka
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Beacon - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `af59d7f17627`

### ASM-CHANGE-MGMT-PRJ-BEACON-2026-03-1

- **Check** CHK-CHANGE-MGMT-PRJ-BEACON-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by K. Tanaka
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Beacon - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `d90fd1190b94`

### ASM-CHANGE-MGMT-PRJ-CORAL-2026-01-1

- **Check** CHK-CHANGE-MGMT-PRJ-CORAL-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by M. Dubois
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Coral - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `27ddd4515580`

### ASM-CHANGE-MGMT-PRJ-CORAL-2026-02-1

- **Check** CHK-CHANGE-MGMT-PRJ-CORAL-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by M. Dubois
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Coral - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `9f771b6b48ec`

### ASM-CHANGE-MGMT-PRJ-CORAL-2026-03-1

- **Check** CHK-CHANGE-MGMT-PRJ-CORAL-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by M. Dubois
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Project Coral - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `4220fb9e1335`

### ASM-CHANGE-MGMT-PROC-2026-01-1

- **Check** CHK-CHANGE-MGMT-PROC-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Procurement - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `dbd6b946f302`

### ASM-CHANGE-MGMT-PROC-2026-02-1

- **Check** CHK-CHANGE-MGMT-PROC-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Procurement - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `e210c065ceb3`

### ASM-CHANGE-MGMT-PROC-2026-03-1

- **Check** CHK-CHANGE-MGMT-PROC-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Change management approval - Procurement - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `d907e0bd06032751` · evidence `b988b3e6791a`

### ASM-CRYPTO-KEY-CUSTOPS-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - Customer Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `0ea4c96a76b0`

### ASM-CRYPTO-KEY-HR-2026-Q1-1 *(superseded by ASM-CRYPTO-KEY-HR-2026-Q1-2)*

- **Check** CHK-CRYPTO-KEY-HR-2026-Q1  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `no_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** No evidence was submitted for 2026-Q1 against Encryption key rotation. The check fell due on 2026-04-15.
- **Gap** No evidence on file for 2026-Q1.

### ASM-CRYPTO-KEY-HR-2026-Q1-2

- **Check** CHK-CRYPTO-KEY-HR-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - AREA-HR - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `d9e45f8623eb`

### ASM-CRYPTO-KEY-ITSVC-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-ITSVC-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - IT Services - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `5bb8cafd5eac`

### ASM-CRYPTO-KEY-MKTG-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-MKTG-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - Marketing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `abc386ba57f4`

### ASM-CRYPTO-KEY-PAYMENTS-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - Payments Processing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `8a57a1b05c0a`

### ASM-CRYPTO-KEY-PRJ-ATLAS-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-PRJ-ATLAS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - Project Atlas - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `a2c595190d6a`

### ASM-CRYPTO-KEY-PRJ-CORAL-2026-Q1-1

- **Check** CHK-CRYPTO-KEY-PRJ-CORAL-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by M. Dubois
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Encryption key rotation - Project Coral - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `cb65a4e42e04d7a9` · evidence `db87bea16e7e`

### ASM-CUST-COMPLAINTS-CUSTOPS-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Customer Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `d0ba991b3ef2`

### ASM-CUST-COMPLAINTS-CUSTOPS-2026-02-1

- **Check** CHK-CUST-COMPLAINTS-CUSTOPS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Customer Operations - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `96a8c3166d1e`

### ASM-CUST-COMPLAINTS-CUSTOPS-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-CUSTOPS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Customer Operations - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `2e33f0ad6253`

### ASM-CUST-COMPLAINTS-MKTG-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-MKTG-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Marketing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `5be14ccc0029`

### ASM-CUST-COMPLAINTS-MKTG-2026-02-1

- **Check** CHK-CUST-COMPLAINTS-MKTG-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Marketing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `073e472e1880`

### ASM-CUST-COMPLAINTS-MKTG-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-MKTG-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Marketing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `57723f7e64ab`

### ASM-CUST-COMPLAINTS-PAYMENTS-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Payments Processing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `c4af24a4bf3f`

### ASM-CUST-COMPLAINTS-PAYMENTS-2026-02-1

- **Check** CHK-CUST-COMPLAINTS-PAYMENTS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Payments Processing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `f6639783c704`

### ASM-CUST-COMPLAINTS-PAYMENTS-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Payments Processing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `4b469f43e1a8`

### ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-01-1

- **Check** CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Project Atlas - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `2c4f410b69f9`

### ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-1 *(superseded by ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-2)*

- **Check** CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-02  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by E. Vasquez
- **Rationale** Evidence is dated 2025-11-18, 102 days before 2026-02 closed, exceeding the 45 day freshness window for Customer complaint handling SLA.
- **Gap** Evidence is 102 days old against a 45 day limit.

### ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-2

- **Check** CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-02  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by E. Vasquez
- **Rationale** The remediation is dated 2025-12-26, 64 days before the period closed, outside the 45 day freshness window.
- **Gap** Remediation evidence is 64 days old.

### ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-03-1

- **Check** CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Customer complaint handling SLA - Project Atlas - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `659a8612298e211b` · evidence `2dd2449756a1`

### ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1 *(superseded by ASM-DATA-RETENTION-CUSTOPS-2026-Q1-2)*

- **Check** CHK-DATA-RETENTION-CUSTOPS-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 1. No retention sweep was run in this period.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `545befb1270b`

### ASM-DATA-RETENTION-CUSTOPS-2026-Q1-2

- **Check** CHK-DATA-RETENTION-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - Customer Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `ab2c42e479ae`

### ASM-DATA-RETENTION-HR-2026-Q1-1

- **Check** CHK-DATA-RETENTION-HR-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - People Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `6cb7ca6299c9`

### ASM-DATA-RETENTION-ITSVC-2026-Q1-1

- **Check** CHK-DATA-RETENTION-ITSVC-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - IT Services - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `12bac1e489d3`

### ASM-DATA-RETENTION-ITSVC-2026-Q2-1 *(superseded by ASM-DATA-RETENTION-ITSVC-2026-Q2-2)*

- **Check** CHK-DATA-RETENTION-ITSVC-2026-Q2  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Evidence is dated 2025-11-22, 220 days before 2026-Q2 closed, exceeding the 100 day freshness window for Data retention schedule adherence.
- **Gap** Evidence is 220 days old against a 100 day limit.

### ASM-DATA-RETENTION-ITSVC-2026-Q2-2

- **Check** CHK-DATA-RETENTION-ITSVC-2026-Q2  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** The remediation is dated 2025-12-11, 201 days before the period closed, outside the 100 day freshness window.
- **Gap** Remediation evidence is 201 days old.

### ASM-DATA-RETENTION-MKTG-2026-Q1-1

- **Check** CHK-DATA-RETENTION-MKTG-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - Marketing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `da2d2fa01739`

### ASM-DATA-RETENTION-PAYMENTS-2026-Q1-1

- **Check** CHK-DATA-RETENTION-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - Payments Processing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `82406f041979`

### ASM-DATA-RETENTION-PRJ-ATLAS-2026-Q1-1

- **Check** CHK-DATA-RETENTION-PRJ-ATLAS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - Project Atlas - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `214858670294`

### ASM-DATA-RETENTION-PRJ-CORAL-2026-Q1-1

- **Check** CHK-DATA-RETENTION-PRJ-CORAL-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by M. Dubois
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Data retention schedule adherence - Project Coral - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `2e10efc5c60f2692` · evidence `255465f89c11`

### ASM-DPIA-MKTG-2026-1 *(superseded by ASM-DPIA-MKTG-2026-2)*

- **Check** CHK-DPIA-MKTG-2026  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by J. Alvarez
- **Rationale** Evidence is dated 2024-10-28, 794 days before 2026 closed, exceeding the 400 day freshness window for Data protection impact assessment currency.
- **Gap** Evidence is 794 days old against a 400 day limit.

### ASM-DPIA-MKTG-2026-2 *(superseded by ASM-DPIA-MKTG-2026-3)*

- **Check** CHK-DPIA-MKTG-2026  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by J. Alvarez
- **Rationale** The remediation is dated 2024-11-20, 771 days before the period closed, outside the 400 day freshness window.
- **Gap** Remediation evidence is 771 days old.

### ASM-DPIA-MKTG-2026-3

- **Check** CHK-DPIA-MKTG-2026  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-02-27 by J. Alvarez
- **Rationale** The remediation is dated 2024-12-04, 757 days before the period closed, outside the 400 day freshness window.
- **Gap** Remediation evidence is 757 days old.

### ASM-INCIDENT-PM-CUSTOPS-2026-01-1

- **Check** CHK-INCIDENT-PM-CUSTOPS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Customer Operations - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `73fe82101ac2`

### ASM-INCIDENT-PM-CUSTOPS-2026-02-1

- **Check** CHK-INCIDENT-PM-CUSTOPS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Customer Operations - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `6e7aa8a18185`

### ASM-INCIDENT-PM-CUSTOPS-2026-03-1

- **Check** CHK-INCIDENT-PM-CUSTOPS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Customer Operations - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `8178a32d172f`

### ASM-INCIDENT-PM-FINREP-2026-01-1

- **Check** CHK-INCIDENT-PM-FINREP-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Financial Reporting - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `f450c54d90c7`

### ASM-INCIDENT-PM-FINREP-2026-02-1 *(superseded by ASM-INCIDENT-PM-FINREP-2026-02-2)*

- **Check** CHK-INCIDENT-PM-FINREP-2026-02  
- **Verdict** `insufficient_evidence` · confidence 1.0 · decided by `wrong_evidence_type`  
- **Human review** no  
- **Recorded** 2026-03-29 by A. Novak
- **Rationale** The submission is a retention_review, but Incident post-mortem completion requires incident_postmortem. The criteria cannot be assessed against it.
- **Gap** Wrong evidence type: retention_review.

### ASM-INCIDENT-PM-FINREP-2026-02-2

- **Check** CHK-INCIDENT-PM-FINREP-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Financial Reporting - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `d9ef8df4b934`

### ASM-INCIDENT-PM-FINREP-2026-03-1

- **Check** CHK-INCIDENT-PM-FINREP-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Financial Reporting - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `57e6deeda3f7`

### ASM-INCIDENT-PM-ITSVC-2026-01-1 *(superseded by ASM-INCIDENT-PM-ITSVC-2026-01-2)*

- **Check** CHK-INCIDENT-PM-ITSVC-2026-01  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by C. Brennan
- **Rationale** Evidence is dated 2025-10-18, 105 days before 2026-01 closed, exceeding the 45 day freshness window for Incident post-mortem completion.
- **Gap** Evidence is 105 days old against a 45 day limit.

### ASM-INCIDENT-PM-ITSVC-2026-01-2

- **Check** CHK-INCIDENT-PM-ITSVC-2026-01  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-01-28 by C. Brennan
- **Rationale** The remediation is dated 2025-11-12, 80 days before the period closed, outside the 45 day freshness window.
- **Gap** Remediation evidence is 80 days old.

### ASM-INCIDENT-PM-ITSVC-2026-02-1

- **Check** CHK-INCIDENT-PM-ITSVC-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - IT Services - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `1287dd322d9e`

### ASM-INCIDENT-PM-ITSVC-2026-03-1

- **Check** CHK-INCIDENT-PM-ITSVC-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - IT Services - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `f4d4eadb9cb0`

### ASM-INCIDENT-PM-PAYMENTS-2026-01-1

- **Check** CHK-INCIDENT-PM-PAYMENTS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Payments Processing - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `218fa2612934`

### ASM-INCIDENT-PM-PAYMENTS-2026-02-1

- **Check** CHK-INCIDENT-PM-PAYMENTS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Payments Processing - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `ad5bbf033cc6`

### ASM-INCIDENT-PM-PAYMENTS-2026-03-1

- **Check** CHK-INCIDENT-PM-PAYMENTS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Payments Processing - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `9898f663b088`

### ASM-INCIDENT-PM-PLATFORM-2026-01-1 *(superseded by ASM-INCIDENT-PM-PLATFORM-2026-01-2)*

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-01  
- **Verdict** `partial` · confidence 0.62 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by N. Iyer
- **Rationale** A criterion is only partially evidenced.
- **Cited evidence** > 3. 9 of 4 carried-in corrective actions were closed; the rest remain open past their due date.
- **Gap** A clause is addressed but not completed.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `39bece785c02`

### ASM-INCIDENT-PM-PLATFORM-2026-01-2

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Platform Engineering - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `6bc87b959764`

### ASM-INCIDENT-PM-PLATFORM-2026-02-1 *(superseded by ASM-INCIDENT-PM-PLATFORM-2026-02-2)*

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-02  
- **Verdict** `partial` · confidence 0.62 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by N. Iyer
- **Rationale** A criterion is only partially evidenced.
- **Cited evidence** > 3. 22 of 3 carried-in corrective actions were closed; the rest remain open past their due date.
- **Gap** A clause is addressed but not completed.
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `32b174d369f0`

### ASM-INCIDENT-PM-PLATFORM-2026-02-2

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Platform Engineering - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `90bab3c8fa1f`

### ASM-INCIDENT-PM-PLATFORM-2026-03-1

- **Check** CHK-INCIDENT-PM-PLATFORM-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Platform Engineering - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `63c10dd88637`

### ASM-INCIDENT-PM-PRJ-ATLAS-2026-01-1

- **Check** CHK-INCIDENT-PM-PRJ-ATLAS-2026-01  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-02-27 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Project Atlas - 2026-01
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `ff26b7d306c7`

### ASM-INCIDENT-PM-PRJ-ATLAS-2026-02-1

- **Check** CHK-INCIDENT-PM-PRJ-ATLAS-2026-02  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-03-29 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Project Atlas - 2026-02
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `b1b63951e3e0`

### ASM-INCIDENT-PM-PRJ-ATLAS-2026-03-1

- **Check** CHK-INCIDENT-PM-PRJ-ATLAS-2026-03  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Incident post-mortem completion - Project Atlas - 2026-03
- **Provenance** prompt `assessment_v2` · criteria `a3f9714ed8d5f12e` · evidence `1228cb18886e`

### ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-1 *(superseded by ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-2)*

- **Check** CHK-INCIDENT-PM-PRJ-ATLAS-2026-04  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** Evidence is dated 2026-01-16, 104 days before 2026-04 closed, exceeding the 45 day freshness window for Incident post-mortem completion.
- **Gap** Evidence is 104 days old against a 45 day limit.

### ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-2

- **Check** CHK-INCIDENT-PM-PRJ-ATLAS-2026-04  
- **Verdict** `gap` · confidence 1.0 · decided by `stale_evidence`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** The remediation is dated 2026-01-30, 90 days before the period closed, outside the 45 day freshness window.
- **Gap** Remediation evidence is 90 days old.

### ASM-THIRD-PARTY-ACCESS-HR-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-HR-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - People Operations - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `159831deb276`

### ASM-THIRD-PARTY-ACCESS-ITSVC-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-ITSVC-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - IT Services - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `fdeffc21a0ca`

### ASM-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - Payments Processing - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `8ea8a48133b2`

### ASM-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1  
- **Verdict** `gap` · confidence 0.88 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** A criterion is contradicted by the evidence.
- **Cited evidence** > 1. No third-party accounts were recertified this quarter.
- **Gap** A required clause is not satisfied.
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `d5a47858c55e`

### ASM-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by K. Tanaka
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - Project Beacon - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `a3e18f70048f`

### ASM-THIRD-PARTY-ACCESS-PROC-2026-Q1-1

- **Check** CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1  
- **Verdict** `compliant` · confidence 0.91 · decided by `s3_model`  
- **Human review** no  
- **Recorded** 2026-04-28 by S. Haugen
- **Rationale** Every criterion is addressed by the evidence.
- **Cited evidence** > Third-party access recertification - Procurement - 2026-Q1
- **Provenance** prompt `assessment_v2` · criteria `d5b0659e0679570c` · evidence `df544e05b67e`

### ASM-TRAINING-CUSTOPS-2026-Q1-1

- **Check** CHK-TRAINING-CUSTOPS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by R. Mehta
- **Rationale** All thresholds met: completion_pct was 98.7 against a required at least 95.0; overdue_staff was 3 against a required at most 5.
- **Cited evidence** > "completion_pct": 98.7
- **Cited evidence** > "overdue_staff": 3

### ASM-TRAINING-FINREP-2026-Q1-1

- **Check** CHK-TRAINING-FINREP-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by A. Novak
- **Rationale** All thresholds met: completion_pct was 99.0 against a required at least 95.0; overdue_staff was 4 against a required at most 5.
- **Cited evidence** > "completion_pct": 99.0
- **Cited evidence** > "overdue_staff": 4

### ASM-TRAINING-HR-2026-Q1-1

- **Check** CHK-TRAINING-HR-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by D. Ferreira
- **Rationale** All thresholds met: completion_pct was 100.0 against a required at least 95.0; overdue_staff was 0 against a required at most 5.
- **Cited evidence** > "completion_pct": 100.0
- **Cited evidence** > "overdue_staff": 0

### ASM-TRAINING-ITSVC-2026-Q1-1

- **Check** CHK-TRAINING-ITSVC-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by C. Brennan
- **Rationale** All thresholds met: completion_pct was 99.3 against a required at least 95.0; overdue_staff was 2 against a required at most 5.
- **Cited evidence** > "completion_pct": 99.3
- **Cited evidence** > "overdue_staff": 2

### ASM-TRAINING-MKTG-2026-Q1-1

- **Check** CHK-TRAINING-MKTG-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by J. Alvarez
- **Rationale** All thresholds met: completion_pct was 98.4 against a required at least 95.0; overdue_staff was 5 against a required at most 5.
- **Cited evidence** > "completion_pct": 98.4
- **Cited evidence** > "overdue_staff": 5

### ASM-TRAINING-PAYMENTS-2026-Q1-1

- **Check** CHK-TRAINING-PAYMENTS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by L. Okafor
- **Rationale** All thresholds met: completion_pct was 98.7 against a required at least 95.0; overdue_staff was 4 against a required at most 5.
- **Cited evidence** > "completion_pct": 98.7
- **Cited evidence** > "overdue_staff": 4

### ASM-TRAINING-PLATFORM-2026-Q1-1

- **Check** CHK-TRAINING-PLATFORM-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by N. Iyer
- **Rationale** All thresholds met: completion_pct was 100.0 against a required at least 95.0; overdue_staff was 0 against a required at most 5.
- **Cited evidence** > "completion_pct": 100.0
- **Cited evidence** > "overdue_staff": 0

### ASM-TRAINING-PRJ-ATLAS-2026-Q1-1

- **Check** CHK-TRAINING-PRJ-ATLAS-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by E. Vasquez
- **Rationale** All thresholds met: completion_pct was 100.0 against a required at least 95.0; overdue_staff was 0 against a required at most 5.
- **Cited evidence** > "completion_pct": 100.0
- **Cited evidence** > "overdue_staff": 0

### ASM-TRAINING-PRJ-BEACON-2026-Q1-1

- **Check** CHK-TRAINING-PRJ-BEACON-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by K. Tanaka
- **Rationale** All thresholds met: completion_pct was 98.5 against a required at least 95.0; overdue_staff was 3 against a required at most 5.
- **Cited evidence** > "completion_pct": 98.5
- **Cited evidence** > "overdue_staff": 3

### ASM-TRAINING-PRJ-CORAL-2026-Q1-1

- **Check** CHK-TRAINING-PRJ-CORAL-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by M. Dubois
- **Rationale** All thresholds met: completion_pct was 98.8 against a required at least 95.0; overdue_staff was 5 against a required at most 5.
- **Cited evidence** > "completion_pct": 98.8
- **Cited evidence** > "overdue_staff": 5

### ASM-TRAINING-PROC-2026-Q1-1

- **Check** CHK-TRAINING-PROC-2026-Q1  
- **Verdict** `compliant` · confidence 1.0 · decided by `structured_threshold`  
- **Human review** no  
- **Recorded** 2026-04-28 by S. Haugen
- **Rationale** All thresholds met: completion_pct was 100.0 against a required at least 95.0; overdue_staff was 0 against a required at most 5.
- **Cited evidence** > "completion_pct": 100.0
- **Cited evidence** > "overdue_staff": 0

## 4. Finding register

### FND-ACCESS-EXPORT-HR-2026-Q1 — open

- **Raised** 2026-04-28 · overdue · severity **Minor**  
- **Owner** D. Ferreira (AREA-HR) · target 2026-05-12  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (D. Ferreira) → severity Minor (ID-PA-KAUR)

### FND-ACCESS-EXPORT-PAYMENTS-2026-Q1 — open

- **Raised** 2026-04-28 · overdue · severity **Major**  
- **Owner** L. Okafor (AREA-PAYMENTS) · target 2026-05-01  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (L. Okafor) → severity Major (ID-PA-KAUR)

### FND-ACCESS-REVIEW-CUSTOPS-2026-Q1 — closed

- **Raised** 2026-04-28 · gap · severity **Major**  
- **Owner** R. Mehta (AREA-CUSTOPS) · target 2026-05-05  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0808 filed by ID-MEHTA → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-2 supersedes ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1: gap -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0808
- **Closed** 2026-04-28 — Remediation accepted. ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-2 supersedes ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1: gap -> compliant, decided by s3_model.
- **History** raised (R. Mehta) → severity Major (ID-PA-KAUR) → owner: implemented (ID-MEHTA) → closed (ID-PA-KAUR)

### FND-BACKUP-VERIFY-PLATFORM-2026-03 — open

- **Raised** 2026-04-28 · gap · severity **Major**  
- **Owner** N. Iyer (AREA-PLATFORM) · target 2026-05-01  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (N. Iyer) → severity Major (ID-PA-KAUR)

### FND-CHANGE-MGMT-FINREP-2026-02 — closed

- **Raised** 2026-03-29 · gap · severity **Minor**  
- **Owner** A. Novak (AREA-FINREP) · target 2026-04-12  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0840 filed by ID-NOVAK → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-CHANGE-MGMT-FINREP-2026-02-2 supersedes ASM-CHANGE-MGMT-FINREP-2026-02-1: gap -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0840
- **Closed** 2026-03-29 — Remediation accepted. ASM-CHANGE-MGMT-FINREP-2026-02-2 supersedes ASM-CHANGE-MGMT-FINREP-2026-02-1: gap -> compliant, decided by s3_model.
- **History** raised (A. Novak) → severity Minor (ID-PA-KAUR) → owner: implemented (ID-NOVAK) → closed (ID-PA-KAUR)

### FND-CHANGE-MGMT-MKTG-2026-02 — closed

- **Raised** 2026-03-29 · gap · severity **Observation**  
- **Owner** J. Alvarez (AREA-MKTG) · target 2026-04-26  
- **Chased** 1 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0848 filed by ID-ALVAREZ → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-CHANGE-MGMT-MKTG-2026-02-2 supersedes ASM-CHANGE-MGMT-MKTG-2026-02-1: gap -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0848
- **Closed** 2026-04-28 — Remediation accepted. ASM-CHANGE-MGMT-MKTG-2026-02-2 supersedes ASM-CHANGE-MGMT-MKTG-2026-02-1: gap -> compliant, decided by s3_model.
- **History** raised (J. Alvarez) → severity Observation (ID-PA-KAUR) → owner: implemented (ID-ALVAREZ) → closed (ID-PA-KAUR)

### FND-CHANGE-MGMT-PRJ-BEACON-2026-02 — closed

- **Raised** 2026-03-29 · gap · severity **Minor**  
- **Owner** K. Tanaka (AREA-PRJ-BEACON) · target 2026-04-12  
- **Chased** 1 reminder(s) · 2 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0866 filed by ID-TANAKA → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-2 supersedes ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1: gap -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0866
- **Closed** 2026-04-28 — Remediation accepted. ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-2 supersedes ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1: gap -> compliant, decided by s3_model.
- **History** raised (K. Tanaka) → severity Minor (ID-PA-KAUR) → escalated L1 (N. Iyer) → escalated L2 (H. Lindqvist) → owner: implemented (ID-TANAKA) → closed (ID-PA-KAUR)

### FND-CRYPTO-KEY-HR-2026-Q1 — closed

- **Raised** 2026-04-28 · overdue · severity **Minor**  
- **Owner** D. Ferreira (AREA-HR) · target 2026-05-12  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-UI-0960 filed by ID-FERREIRA → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-CRYPTO-KEY-HR-2026-Q1-2 supersedes ASM-CRYPTO-KEY-HR-2026-Q1-1: insufficient_evidence -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-UI-0960
- **Closed** 2026-04-28 — Remediation accepted. ASM-CRYPTO-KEY-HR-2026-Q1-2 supersedes ASM-CRYPTO-KEY-HR-2026-Q1-1: insufficient_evidence -> compliant, decided by s3_model.
- **History** raised (D. Ferreira) → severity Minor (ID-PA-KAUR) → owner: implemented (ID-FERREIRA) → closed (ID-PA-KAUR)

### FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 — open

- **Raised** 2026-02-27 · gap · severity **Minor**  
- **Owner** E. Vasquez (AREA-PRJ-ATLAS) · target 2026-03-13  
- **Chased** 2 reminder(s) · 2 escalation(s) · 1 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0893 filed by ID-VASQUEZ → **insufficient** by ID-PA-KAUR  
  _Evidence does not clear the finding: still gap. Resubmit._
- **Remediation submitted** EV-SUB-0893
- **History** raised (E. Vasquez) → severity Minor (ID-PA-KAUR) → owner: implemented (ID-VASQUEZ) → evidence insufficient (ID-PA-KAUR) → escalated L1 (N. Iyer) → escalated L2 (H. Lindqvist)

### FND-DATA-RETENTION-CUSTOPS-2026-Q1 — closed

- **Raised** 2026-04-28 · gap · severity **Major**  
- **Owner** R. Mehta (AREA-CUSTOPS) · target 2026-05-05  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0894 filed by ID-MEHTA → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-DATA-RETENTION-CUSTOPS-2026-Q1-2 supersedes ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1: gap -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0894
- **Closed** 2026-04-28 — Remediation accepted. ASM-DATA-RETENTION-CUSTOPS-2026-Q1-2 supersedes ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1: gap -> compliant, decided by s3_model.
- **History** raised (R. Mehta) → severity Major (ID-PA-KAUR) → owner: implemented (ID-MEHTA) → closed (ID-PA-KAUR)

### FND-DATA-RETENTION-ITSVC-2026-Q2 — open

- **Raised** 2026-04-28 · gap · severity **Major**  
- **Owner** C. Brennan (AREA-ITSVC) · target 2026-05-05  
- **Chased** 0 reminder(s) · 0 escalation(s) · 1 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0898 filed by ID-BRENNAN → **insufficient** by ID-PA-KAUR  
  _Evidence does not clear the finding: still gap. Resubmit._
- **Remediation submitted** EV-SUB-0898
- **History** raised (C. Brennan) → severity Major (ID-PA-KAUR) → owner: implemented (ID-BRENNAN) → evidence insufficient (ID-PA-KAUR)

### FND-DOC-2026-09-01 — closed

- **Raised** 2026-09-18 · ? · severity **Major**  
- **Owner** S. Haugen (AREA-PROC) · target 2026-09-25  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (S. Haugen) → closed (ID-PA-KAUR)

### FND-DOC-2026-09-02 — closed

- **Raised** 2026-09-18 · ? · severity **Minor**  
- **Owner** A. Novak (AREA-FINREP) · target 2026-10-02  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (A. Novak) → closed (ID-PA-KAUR)

### FND-DOC-2026-09-03 — closed

- **Raised** 2026-09-18 · ? · severity **Minor**  
- **Owner** C. Brennan (AREA-ITSVC) · target 2026-10-02  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (C. Brennan) → closed (ID-PA-KAUR)

### FND-DPIA-MKTG-2026 — open

- **Raised** 2026-01-28 · gap · severity **Observation**  
- **Owner** J. Alvarez (AREA-MKTG) · target 2026-02-25  
- **Chased** 3 reminder(s) · 2 escalation(s) · 2 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0903 filed by ID-ALVAREZ → **insufficient** by ID-PA-KAUR  
  _Evidence does not clear the finding: still gap. Resubmit._
- **Round 2** EV-SUB-0904 filed by ID-ALVAREZ → **insufficient** by ID-PA-KAUR  
  _Evidence does not clear the finding: still gap. Resubmit._
- **Remediation submitted** EV-SUB-0904
- **History** raised (J. Alvarez) → severity Observation (ID-PA-KAUR) → owner: implemented (ID-ALVAREZ) → evidence insufficient (ID-PA-KAUR) → owner: implemented (ID-ALVAREZ) → evidence insufficient (ID-PA-KAUR) → escalated L1 (M. Castellanos) → escalated L2 (H. Lindqvist)

### FND-IA-2026-H1-01 — closed

- **Raised** 2026-03-20 · ? · severity **Major**  
- **Owner** L. Okafor (AREA-PAYMENTS) · target 2026-03-23  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (L. Okafor) → closed (ID-PA-OSEI)

### FND-IA-2026-H1-02 — open

- **Raised** 2026-03-20 · ? · severity **Minor**  
- **Owner** R. Mehta (AREA-CUSTOPS) · target 2026-04-03  
- **Chased** 1 reminder(s) · 2 escalation(s) · 0 insufficient round(s)
- **History** raised (R. Mehta) → escalated L1 (M. Castellanos) → escalated L2 (H. Lindqvist)

### FND-IA-2026-H1-03 — closed

- **Raised** 2026-03-20 · ? · severity **Observation**  
- **Owner** D. Ferreira (AREA-HR) · target 2026-04-17  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (D. Ferreira) → closed (ID-PA-OSEI)

### FND-IA-2026-H2-01 — open

- **Raised** 2026-11-13 · ? · severity **Major**  
- **Owner** C. Brennan (AREA-ITSVC) · target 2026-11-20  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (C. Brennan)

### FND-IA-2026-H2-02 — closed

- **Raised** 2026-11-13 · ? · severity **Observation**  
- **Owner** J. Alvarez (AREA-MKTG) · target 2026-12-11  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (J. Alvarez) → closed (ID-PA-OSEI)

### FND-IA-2026-H2-03 — closed

- **Raised** 2026-11-13 · ? · severity **Minor**  
- **Owner** M. Dubois (AREA-PRJ-CORAL) · target 2026-11-27  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (M. Dubois) → closed (ID-PA-OSEI)

### FND-INCIDENT-PM-FINREP-2026-02 — closed

- **Raised** 2026-03-29 · gap · severity **Minor**  
- **Owner** A. Novak (AREA-FINREP) · target 2026-04-12  
- **Chased** 1 reminder(s) · 2 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0911 filed by ID-NOVAK → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-INCIDENT-PM-FINREP-2026-02-2 supersedes ASM-INCIDENT-PM-FINREP-2026-02-1: insufficient_evidence -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0911
- **Closed** 2026-04-28 — Remediation accepted. ASM-INCIDENT-PM-FINREP-2026-02-2 supersedes ASM-INCIDENT-PM-FINREP-2026-02-1: insufficient_evidence -> compliant, decided by s3_model.
- **History** raised (A. Novak) → severity Minor (ID-PA-KAUR) → escalated L1 (H. Lindqvist) → escalated L2 (H. Lindqvist) → owner: implemented (ID-NOVAK) → closed (ID-PA-KAUR)

### FND-INCIDENT-PM-ITSVC-2026-01 — open

- **Raised** 2026-01-28 · gap · severity **Minor**  
- **Owner** C. Brennan (AREA-ITSVC) · target 2026-02-11  
- **Chased** 3 reminder(s) · 2 escalation(s) · 1 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0915 filed by ID-BRENNAN → **insufficient** by ID-PA-KAUR  
  _Evidence does not clear the finding: still gap. Resubmit._
- **Remediation submitted** EV-SUB-0915
- **History** raised (C. Brennan) → severity Minor (ID-PA-KAUR) → owner: implemented (ID-BRENNAN) → evidence insufficient (ID-PA-KAUR) → escalated L1 (M. Castellanos) → escalated L2 (H. Lindqvist)

### FND-INCIDENT-PM-PLATFORM-2026-01 — closed

- **Raised** 2026-02-27 · gap · severity **Minor**  
- **Owner** N. Iyer (AREA-PLATFORM) · target 2026-03-13  
- **Chased** 1 reminder(s) · 2 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0919 filed by ID-IYER → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-INCIDENT-PM-PLATFORM-2026-01-2 supersedes ASM-INCIDENT-PM-PLATFORM-2026-01-1: partial -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0919
- **Closed** 2026-03-29 — Remediation accepted. ASM-INCIDENT-PM-PLATFORM-2026-01-2 supersedes ASM-INCIDENT-PM-PLATFORM-2026-01-1: partial -> compliant, decided by s3_model.
- **History** raised (N. Iyer) → severity Minor (ID-PA-KAUR) → escalated L1 (H. Lindqvist) → escalated L2 (H. Lindqvist) → owner: implemented (ID-IYER) → closed (ID-PA-KAUR)

### FND-INCIDENT-PM-PLATFORM-2026-02 — closed

- **Raised** 2026-03-29 · gap · severity **Minor**  
- **Owner** N. Iyer (AREA-PLATFORM) · target 2026-04-12  
- **Chased** 1 reminder(s) · 2 escalation(s) · 0 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0920 filed by ID-IYER → **accepted** by ID-PA-KAUR  
  _Remediation accepted. ASM-INCIDENT-PM-PLATFORM-2026-02-2 supersedes ASM-INCIDENT-PM-PLATFORM-2026-02-1: partial -> compliant, decided by s3_model._
- **Remediation submitted** EV-SUB-0920
- **Closed** 2026-04-28 — Remediation accepted. ASM-INCIDENT-PM-PLATFORM-2026-02-2 supersedes ASM-INCIDENT-PM-PLATFORM-2026-02-1: partial -> compliant, decided by s3_model.
- **History** raised (N. Iyer) → severity Minor (ID-PA-KAUR) → escalated L1 (H. Lindqvist) → escalated L2 (H. Lindqvist) → owner: implemented (ID-IYER) → closed (ID-PA-KAUR)

### FND-INCIDENT-PM-PRJ-ATLAS-2026-04 — open

- **Raised** 2026-04-28 · gap · severity **Major**  
- **Owner** E. Vasquez (AREA-PRJ-ATLAS) · target 2026-05-01  
- **Chased** 0 reminder(s) · 0 escalation(s) · 1 insufficient round(s)
- **Owner progress** implemented (self-reported)
- **Round 1** EV-SUB-0926 filed by ID-VASQUEZ → **insufficient** by ID-PA-KAUR  
  _Evidence does not clear the finding: still gap. Resubmit._
- **Remediation submitted** EV-SUB-0926
- **History** raised (E. Vasquez) → severity Major (ID-PA-KAUR) → owner: implemented (ID-VASQUEZ) → evidence insufficient (ID-PA-KAUR)

### FND-QA-2026-Q2-01 — closed

- **Raised** 2026-05-22 · ? · severity **Major**  
- **Owner** N. Iyer (AREA-PLATFORM) · target 2026-05-25  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (N. Iyer) → closed (ID-PA-KAUR)

### FND-QA-2026-Q2-02 — closed

- **Raised** 2026-05-22 · ? · severity **Minor**  
- **Owner** E. Vasquez (AREA-PRJ-ATLAS) · target 2026-06-05  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (E. Vasquez) → closed (ID-PA-KAUR)

### FND-QA-2027-Q1-01 — open

- **Raised** 2027-02-19 · ? · severity **Major**  
- **Owner** L. Okafor (AREA-PAYMENTS) · target 2027-02-22  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (L. Okafor)

### FND-QA-2027-Q1-02 — closed

- **Raised** 2027-02-19 · ? · severity **Minor**  
- **Owner** K. Tanaka (AREA-PRJ-BEACON) · target 2027-03-05  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (K. Tanaka) → closed (ID-PA-KAUR)

### FND-REL-2026-07-01 — closed

- **Raised** 2026-07-10 · ? · severity **Major**  
- **Owner** E. Vasquez (AREA-PRJ-ATLAS) · target 2026-07-13  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (E. Vasquez) → closed (ID-PA-OSEI)

### FND-REL-2026-07-02 — closed

- **Raised** 2026-07-10 · ? · severity **Observation**  
- **Owner** K. Tanaka (AREA-PRJ-BEACON) · target 2026-08-07  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **Closed** 2026-09-08 — Evidence reviewed and accepted; the agreed action plan was completed and verified.
- **History** raised (K. Tanaka) → closed (ID-PA-OSEI)

### FND-REL-2027-04-01 — open

- **Raised** 2027-04-09 · ? · severity **Major**  
- **Owner** M. Dubois (AREA-PRJ-CORAL) · target 2027-04-16  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (M. Dubois)

### FND-REL-2027-04-02 — open

- **Raised** 2027-04-09 · ? · severity **Observation**  
- **Owner** N. Iyer (AREA-PLATFORM) · target 2027-05-07  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (N. Iyer)

### FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 — open

- **Raised** 2026-04-28 · gap · severity **Major**  
- **Owner** N. Iyer (AREA-PLATFORM) · target 2026-05-01  
- **Chased** 0 reminder(s) · 0 escalation(s) · 0 insufficient round(s)
- **History** raised (N. Iyer) → severity Major (ID-PA-KAUR)

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

1,255 events, in the order they were written.

| # | Timestamp | Actor | Owner | Event | Entity |
|---|---|---|---|---|---|
| 1 | 2026-01-01 00:00:00 | user | Group Risk Committee | exception_registered | ComplianceException:EXC-001 |
| 2 | 2026-01-01 00:00:01 | user | Chief Procurement Officer | exception_registered | ComplianceException:EXC-002 |
| 3 | 2026-01-01 00:00:02 | user | Finance Control Board | exception_registered | ComplianceException:EXC-003 |
| 4 | 2026-01-01 00:00:03 | user | Chief Information Security Officer | exception_registered | ComplianceException:EXC-004 |
| 5 | 2026-01-01 00:00:04 | system | synthetic generator | corpus_seeded | Corpus:20260831 |
| 6 | 2026-03-20 09:00:00 | user | P. Kaur | audit_conducted | ScheduledAudit:AUD-IA-2026-H1 |
| 7 | 2026-03-20 10:00:00 | user | L. Okafor | finding_raised | Finding:FND-IA-2026-H1-01 |
| 8 | 2026-03-20 10:00:00 | user | R. Mehta | finding_raised | Finding:FND-IA-2026-H1-02 |
| 9 | 2026-03-20 10:00:00 | user | D. Ferreira | finding_raised | Finding:FND-IA-2026-H1-03 |
| 10 | 2026-05-22 09:00:00 | user | T. Osei | audit_conducted | ScheduledAudit:AUD-QA-2026-Q2 |
| 11 | 2026-05-22 10:00:00 | user | N. Iyer | finding_raised | Finding:FND-QA-2026-Q2-01 |
| 12 | 2026-05-22 10:00:00 | user | E. Vasquez | finding_raised | Finding:FND-QA-2026-Q2-02 |
| 13 | 2026-07-10 09:00:00 | user | P. Kaur | audit_conducted | ScheduledAudit:AUD-REL-2026-07 |
| 14 | 2026-07-10 10:00:00 | user | E. Vasquez | finding_raised | Finding:FND-REL-2026-07-01 |
| 15 | 2026-07-10 10:00:00 | user | K. Tanaka | finding_raised | Finding:FND-REL-2026-07-02 |
| 16 | 2026-09-18 09:00:00 | user | T. Osei | audit_conducted | ScheduledAudit:AUD-DOC-2026-09 |
| 17 | 2026-09-18 10:00:00 | user | S. Haugen | finding_raised | Finding:FND-DOC-2026-09-01 |
| 18 | 2026-09-18 10:00:00 | user | A. Novak | finding_raised | Finding:FND-DOC-2026-09-02 |
| 19 | 2026-09-18 10:00:00 | user | C. Brennan | finding_raised | Finding:FND-DOC-2026-09-03 |
| 20 | 2026-11-13 09:00:00 | user | P. Kaur | audit_conducted | ScheduledAudit:AUD-IA-2026-H2 |
| 21 | 2026-11-13 10:00:00 | user | C. Brennan | finding_raised | Finding:FND-IA-2026-H2-01 |
| 22 | 2026-11-13 10:00:00 | user | J. Alvarez | finding_raised | Finding:FND-IA-2026-H2-02 |
| 23 | 2026-11-13 10:00:00 | user | M. Dubois | finding_raised | Finding:FND-IA-2026-H2-03 |
| 24 | 2027-02-19 09:00:00 | user | T. Osei | audit_conducted | ScheduledAudit:AUD-QA-2027-Q1 |
| 25 | 2027-02-19 10:00:00 | user | L. Okafor | finding_raised | Finding:FND-QA-2027-Q1-01 |
| 26 | 2027-02-19 10:00:00 | user | K. Tanaka | finding_raised | Finding:FND-QA-2027-Q1-02 |
| 27 | 2027-04-09 09:00:00 | user | P. Kaur | audit_conducted | ScheduledAudit:AUD-REL-2027-04 |
| 28 | 2027-04-09 10:00:00 | user | M. Dubois | finding_raised | Finding:FND-REL-2027-04-01 |
| 29 | 2027-04-09 10:00:00 | user | N. Iyer | finding_raised | Finding:FND-REL-2027-04-02 |
| 30 | 2026-09-08 01:28:41 | user | ID-PA-OSEI | finding_closed | Finding:FND-IA-2026-H1-01 |
| 31 | 2026-09-08 01:28:41 | user | ID-PA-OSEI | finding_closed | Finding:FND-IA-2026-H1-03 |
| 32 | 2026-09-08 01:28:41 | user | ID-PA-KAUR | finding_closed | Finding:FND-QA-2026-Q2-01 |
| 33 | 2026-09-08 01:28:42 | user | ID-PA-KAUR | finding_closed | Finding:FND-QA-2026-Q2-02 |
| 34 | 2026-09-08 01:28:42 | user | ID-PA-OSEI | finding_closed | Finding:FND-REL-2026-07-02 |
| 35 | 2026-09-08 01:28:42 | user | ID-PA-KAUR | finding_closed | Finding:FND-DOC-2026-09-02 |
| 36 | 2026-09-08 01:28:42 | user | ID-PA-KAUR | finding_closed | Finding:FND-DOC-2026-09-03 |
| 37 | 2026-09-08 01:28:43 | user | ID-PA-OSEI | finding_closed | Finding:FND-IA-2026-H2-02 |
| 38 | 2026-09-08 01:28:43 | user | ID-PA-OSEI | finding_closed | Finding:FND-IA-2026-H2-03 |
| 39 | 2026-09-08 01:28:43 | user | ID-PA-KAUR | finding_closed | Finding:FND-QA-2027-Q1-02 |
| 40 | 2026-09-08 01:28:43 | user | ID-PA-OSEI | finding_closed | Finding:FND-REL-2026-07-01 |
| 41 | 2026-09-08 01:28:43 | user | ID-PA-KAUR | finding_closed | Finding:FND-DOC-2026-09-01 |
| 42 | 2026-01-28 02:00:00 | user | user | cycle_started | Cycle:2026-01-28 |
| 43 | 2026-01-28 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1 |
| 44 | 2026-01-28 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1 |
| 45 | 2026-01-28 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 46 | 2026-01-28 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 47 | 2026-01-28 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 48 | 2026-01-28 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 49 | 2026-01-28 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BCP-TEST-CUSTOPS-2026 |
| 50 | 2026-01-28 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-BCP-TEST-CUSTOPS-2026 |
| 51 | 2026-01-28 02:00:09 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-01 |
| 52 | 2026-01-28 02:00:10 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-01 |
| 53 | 2026-01-28 02:00:11 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q1 |
| 54 | 2026-01-28 02:00:12 | system | R. Mehta | notification_logged | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q1 |
| 55 | 2026-01-28 02:00:13 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-01 |
| 56 | 2026-01-28 02:00:14 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-01 |
| 57 | 2026-01-28 02:00:15 | system | R. Mehta | check_instance_created | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 58 | 2026-01-28 02:00:16 | system | R. Mehta | notification_logged | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 59 | 2026-01-28 02:00:17 | system | R. Mehta | check_instance_created | CheckInstance:CHK-DPIA-CUSTOPS-2026 |
| 60 | 2026-01-28 02:00:18 | system | R. Mehta | notification_logged | CheckInstance:CHK-DPIA-CUSTOPS-2026 |
| 61 | 2026-01-28 02:00:19 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-01 |
| 62 | 2026-01-28 02:00:20 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-01 |
| 63 | 2026-01-28 02:00:21 | system | R. Mehta | check_instance_created | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q1 |
| 64 | 2026-01-28 02:00:22 | system | R. Mehta | notification_logged | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q1 |
| 65 | 2026-01-28 02:00:23 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-01 |
| 66 | 2026-01-28 02:00:24 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-01 |
| 67 | 2026-01-28 02:00:25 | system | A. Novak | check_instance_created | CheckInstance:CHK-BCP-TEST-FINREP-2026 |
| 68 | 2026-01-28 02:00:26 | system | A. Novak | notification_logged | CheckInstance:CHK-BCP-TEST-FINREP-2026 |
| 69 | 2026-01-28 02:00:27 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-01 |
| 70 | 2026-01-28 02:00:28 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-01 |
| 71 | 2026-01-28 02:00:29 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-01 |
| 72 | 2026-01-28 02:00:30 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-01 |
| 73 | 2026-01-28 02:00:31 | system | A. Novak | check_instance_created | CheckInstance:CHK-TRAINING-FINREP-2026-Q1 |
| 74 | 2026-01-28 02:00:32 | system | A. Novak | notification_logged | CheckInstance:CHK-TRAINING-FINREP-2026-Q1 |
| 75 | 2026-01-28 02:00:33 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 76 | 2026-01-28 02:00:34 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 77 | 2026-01-28 02:00:35 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q1 |
| 78 | 2026-01-28 02:00:36 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q1 |
| 79 | 2026-01-28 02:00:37 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 80 | 2026-01-28 02:00:38 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 81 | 2026-01-28 02:00:39 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 82 | 2026-01-28 02:00:40 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 83 | 2026-01-28 02:00:41 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q1 |
| 84 | 2026-01-28 02:00:42 | system | D. Ferreira | notification_logged | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q1 |
| 85 | 2026-01-28 02:00:43 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-DPIA-HR-2026 |
| 86 | 2026-01-28 02:00:44 | system | D. Ferreira | notification_logged | CheckInstance:CHK-DPIA-HR-2026 |
| 87 | 2026-01-28 02:00:45 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-HR-2026 |
| 88 | 2026-01-28 02:00:46 | system | D. Ferreira | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-HR-2026 |
| 89 | 2026-01-28 02:00:47 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q1 |
| 90 | 2026-01-28 02:00:48 | system | D. Ferreira | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q1 |
| 91 | 2026-01-28 02:00:49 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-TRAINING-HR-2026-Q1 |
| 92 | 2026-01-28 02:00:50 | system | D. Ferreira | notification_logged | CheckInstance:CHK-TRAINING-HR-2026-Q1 |
| 93 | 2026-01-28 02:00:51 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-VENDOR-DD-HR-2026 |
| 94 | 2026-01-28 02:00:52 | system | D. Ferreira | notification_logged | CheckInstance:CHK-VENDOR-DD-HR-2026 |
| 95 | 2026-01-28 02:00:53 | system | C. Brennan | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-ITSVC-2026-Q1 |
| 96 | 2026-01-28 02:00:54 | system | C. Brennan | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-ITSVC-2026-Q1 |
| 97 | 2026-01-28 02:00:55 | system | C. Brennan | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-ITSVC-2026-Q1 |
| 98 | 2026-01-28 02:00:56 | system | C. Brennan | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-ITSVC-2026-Q1 |
| 99 | 2026-01-28 02:00:57 | system | C. Brennan | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-01 |
| 100 | 2026-01-28 02:00:58 | system | C. Brennan | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-01 |
| 101 | 2026-01-28 02:00:59 | system | C. Brennan | check_instance_created | CheckInstance:CHK-BCP-TEST-ITSVC-2026 |
| 102 | 2026-01-28 02:01:00 | system | C. Brennan | notification_logged | CheckInstance:CHK-BCP-TEST-ITSVC-2026 |
| 103 | 2026-01-28 02:01:01 | system | C. Brennan | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-01 |
| 104 | 2026-01-28 02:01:02 | system | C. Brennan | notification_logged | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-01 |
| 105 | 2026-01-28 02:01:03 | system | C. Brennan | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-ITSVC-2026-Q1 |
| 106 | 2026-01-28 02:01:04 | system | C. Brennan | notification_logged | CheckInstance:CHK-CRYPTO-KEY-ITSVC-2026-Q1 |
| 107 | 2026-01-28 02:01:05 | system | C. Brennan | check_instance_created | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q1 |
| 108 | 2026-01-28 02:01:06 | system | C. Brennan | notification_logged | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q1 |
| 109 | 2026-01-28 02:01:07 | system | C. Brennan | check_instance_created | CheckInstance:CHK-DPIA-ITSVC-2026 |
| 110 | 2026-01-28 02:01:08 | system | C. Brennan | notification_logged | CheckInstance:CHK-DPIA-ITSVC-2026 |
| 111 | 2026-01-28 02:01:09 | system | C. Brennan | check_instance_created | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-01 |
| 112 | 2026-01-28 02:01:10 | system | C. Brennan | notification_logged | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-01 |
| 113 | 2026-01-28 02:01:11 | system | C. Brennan | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-ITSVC-2026 |
| 114 | 2026-01-28 02:01:12 | system | C. Brennan | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-ITSVC-2026 |
| 115 | 2026-01-28 02:01:13 | system | C. Brennan | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-ITSVC-2026-Q1 |
| 116 | 2026-01-28 02:01:14 | system | C. Brennan | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-ITSVC-2026-Q1 |
| 117 | 2026-01-28 02:01:15 | system | C. Brennan | check_instance_created | CheckInstance:CHK-TRAINING-ITSVC-2026-Q1 |
| 118 | 2026-01-28 02:01:16 | system | C. Brennan | notification_logged | CheckInstance:CHK-TRAINING-ITSVC-2026-Q1 |
| 119 | 2026-01-28 02:01:17 | system | C. Brennan | check_instance_created | CheckInstance:CHK-VENDOR-DD-ITSVC-2026 |
| 120 | 2026-01-28 02:01:18 | system | C. Brennan | notification_logged | CheckInstance:CHK-VENDOR-DD-ITSVC-2026 |
| 121 | 2026-01-28 02:01:19 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q1 |
| 122 | 2026-01-28 02:01:20 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q1 |
| 123 | 2026-01-28 02:01:21 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q1 |
| 124 | 2026-01-28 02:01:22 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q1 |
| 125 | 2026-01-28 02:01:23 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 126 | 2026-01-28 02:01:24 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 127 | 2026-01-28 02:01:25 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q1 |
| 128 | 2026-01-28 02:01:26 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q1 |
| 129 | 2026-01-28 02:01:27 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-01 |
| 130 | 2026-01-28 02:01:28 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-01 |
| 131 | 2026-01-28 02:01:29 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q1 |
| 132 | 2026-01-28 02:01:30 | system | J. Alvarez | notification_logged | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q1 |
| 133 | 2026-01-28 02:01:31 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-DPIA-MKTG-2026 |
| 134 | 2026-01-28 02:01:32 | system | J. Alvarez | notification_logged | CheckInstance:CHK-DPIA-MKTG-2026 |
| 135 | 2026-01-28 02:01:33 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-MKTG-2026 |
| 136 | 2026-01-28 02:01:34 | system | J. Alvarez | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-MKTG-2026 |
| 137 | 2026-01-28 02:01:35 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-TRAINING-MKTG-2026-Q1 |
| 138 | 2026-01-28 02:01:36 | system | J. Alvarez | notification_logged | CheckInstance:CHK-TRAINING-MKTG-2026-Q1 |
| 139 | 2026-01-28 02:01:37 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-VENDOR-DD-MKTG-2026 |
| 140 | 2026-01-28 02:01:38 | system | J. Alvarez | notification_logged | CheckInstance:CHK-VENDOR-DD-MKTG-2026 |
| 141 | 2026-01-28 02:01:39 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 142 | 2026-01-28 02:01:40 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 143 | 2026-01-28 02:01:41 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 144 | 2026-01-28 02:01:42 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 145 | 2026-01-28 02:01:43 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-01 |
| 146 | 2026-01-28 02:01:44 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-01 |
| 147 | 2026-01-28 02:01:45 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BCP-TEST-PAYMENTS-2026 |
| 148 | 2026-01-28 02:01:46 | system | L. Okafor | notification_logged | CheckInstance:CHK-BCP-TEST-PAYMENTS-2026 |
| 149 | 2026-01-28 02:01:47 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 150 | 2026-01-28 02:01:48 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 151 | 2026-01-28 02:01:49 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 152 | 2026-01-28 02:01:50 | system | L. Okafor | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 153 | 2026-01-28 02:01:51 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-01 |
| 154 | 2026-01-28 02:01:52 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-01 |
| 155 | 2026-01-28 02:01:53 | system | L. Okafor | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 156 | 2026-01-28 02:01:54 | system | L. Okafor | notification_logged | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 157 | 2026-01-28 02:01:55 | system | L. Okafor | check_instance_created | CheckInstance:CHK-DPIA-PAYMENTS-2026 |
| 158 | 2026-01-28 02:01:56 | system | L. Okafor | notification_logged | CheckInstance:CHK-DPIA-PAYMENTS-2026 |
| 159 | 2026-01-28 02:01:57 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-01 |
| 160 | 2026-01-28 02:01:58 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-01 |
| 161 | 2026-01-28 02:01:59 | system | L. Okafor | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PAYMENTS-2026 |
| 162 | 2026-01-28 02:02:00 | system | L. Okafor | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PAYMENTS-2026 |
| 163 | 2026-01-28 02:02:01 | system | L. Okafor | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1 |
| 164 | 2026-01-28 02:02:02 | system | L. Okafor | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1 |
| 165 | 2026-01-28 02:02:03 | system | L. Okafor | check_instance_created | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q1 |
| 166 | 2026-01-28 02:02:04 | system | L. Okafor | notification_logged | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q1 |
| 167 | 2026-01-28 02:02:05 | system | L. Okafor | check_instance_created | CheckInstance:CHK-VENDOR-DD-PAYMENTS-2026 |
| 168 | 2026-01-28 02:02:06 | system | L. Okafor | notification_logged | CheckInstance:CHK-VENDOR-DD-PAYMENTS-2026 |
| 169 | 2026-01-28 02:02:07 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-01 |
| 170 | 2026-01-28 02:02:08 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-01 |
| 171 | 2026-01-28 02:02:09 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 172 | 2026-01-28 02:02:10 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 173 | 2026-01-28 02:02:11 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 174 | 2026-01-28 02:02:12 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 175 | 2026-01-28 02:02:13 | system | N. Iyer | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PLATFORM-2026 |
| 176 | 2026-01-28 02:02:14 | system | N. Iyer | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PLATFORM-2026 |
| 177 | 2026-01-28 02:02:15 | system | N. Iyer | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 178 | 2026-01-28 02:02:16 | system | N. Iyer | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 179 | 2026-01-28 02:02:17 | system | N. Iyer | check_instance_created | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q1 |
| 180 | 2026-01-28 02:02:18 | system | N. Iyer | notification_logged | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q1 |
| 181 | 2026-01-28 02:02:19 | system | N. Iyer | check_instance_created | CheckInstance:CHK-VENDOR-DD-PLATFORM-2026 |
| 182 | 2026-01-28 02:02:20 | system | N. Iyer | notification_logged | CheckInstance:CHK-VENDOR-DD-PLATFORM-2026 |
| 183 | 2026-01-28 02:02:21 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PRJ-ATLAS-2026-Q1 |
| 184 | 2026-01-28 02:02:22 | system | E. Vasquez | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PRJ-ATLAS-2026-Q1 |
| 185 | 2026-01-28 02:02:23 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PRJ-ATLAS-2026-Q1 |
| 186 | 2026-01-28 02:02:24 | system | E. Vasquez | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PRJ-ATLAS-2026-Q1 |
| 187 | 2026-01-28 02:02:25 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-01 |
| 188 | 2026-01-28 02:02:26 | system | E. Vasquez | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-01 |
| 189 | 2026-01-28 02:02:27 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-BCP-TEST-PRJ-ATLAS-2026 |
| 190 | 2026-01-28 02:02:28 | system | E. Vasquez | notification_logged | CheckInstance:CHK-BCP-TEST-PRJ-ATLAS-2026 |
| 191 | 2026-01-28 02:02:29 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-01 |
| 192 | 2026-01-28 02:02:30 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-01 |
| 193 | 2026-01-28 02:02:31 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PRJ-ATLAS-2026-Q1 |
| 194 | 2026-01-28 02:02:32 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PRJ-ATLAS-2026-Q1 |
| 195 | 2026-01-28 02:02:33 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-01 |
| 196 | 2026-01-28 02:02:34 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-01 |
| 197 | 2026-01-28 02:02:35 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PRJ-ATLAS-2026-Q1 |
| 198 | 2026-01-28 02:02:36 | system | E. Vasquez | notification_logged | CheckInstance:CHK-DATA-RETENTION-PRJ-ATLAS-2026-Q1 |
| 199 | 2026-01-28 02:02:37 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-DPIA-PRJ-ATLAS-2026 |
| 200 | 2026-01-28 02:02:38 | system | E. Vasquez | notification_logged | CheckInstance:CHK-DPIA-PRJ-ATLAS-2026 |
| 201 | 2026-01-28 02:02:39 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-01 |
| 202 | 2026-01-28 02:02:40 | system | E. Vasquez | notification_logged | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-01 |
| 203 | 2026-01-28 02:02:41 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-TRAINING-PRJ-ATLAS-2026-Q1 |
| 204 | 2026-01-28 02:02:42 | system | E. Vasquez | notification_logged | CheckInstance:CHK-TRAINING-PRJ-ATLAS-2026-Q1 |
| 205 | 2026-01-28 02:02:43 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-01 |
| 206 | 2026-01-28 02:02:44 | system | K. Tanaka | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-01 |
| 207 | 2026-01-28 02:02:45 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PRJ-BEACON-2026 |
| 208 | 2026-01-28 02:02:46 | system | K. Tanaka | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PRJ-BEACON-2026 |
| 209 | 2026-01-28 02:02:47 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q1 |
| 210 | 2026-01-28 02:02:48 | system | K. Tanaka | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q1 |
| 211 | 2026-01-28 02:02:49 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-TRAINING-PRJ-BEACON-2026-Q1 |
| 212 | 2026-01-28 02:02:50 | system | K. Tanaka | notification_logged | CheckInstance:CHK-TRAINING-PRJ-BEACON-2026-Q1 |
| 213 | 2026-01-28 02:02:51 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-VENDOR-DD-PRJ-BEACON-2026 |
| 214 | 2026-01-28 02:02:52 | system | K. Tanaka | notification_logged | CheckInstance:CHK-VENDOR-DD-PRJ-BEACON-2026 |
| 215 | 2026-01-28 02:02:53 | system | M. Dubois | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PRJ-CORAL-2026-Q1 |
| 216 | 2026-01-28 02:02:54 | system | M. Dubois | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PRJ-CORAL-2026-Q1 |
| 217 | 2026-01-28 02:02:55 | system | M. Dubois | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PRJ-CORAL-2026-Q1 |
| 218 | 2026-01-28 02:02:56 | system | M. Dubois | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PRJ-CORAL-2026-Q1 |
| 219 | 2026-01-28 02:02:57 | system | M. Dubois | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-01 |
| 220 | 2026-01-28 02:02:58 | system | M. Dubois | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-01 |
| 221 | 2026-01-28 02:02:59 | system | M. Dubois | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PRJ-CORAL-2026-Q1 |
| 222 | 2026-01-28 02:03:00 | system | M. Dubois | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PRJ-CORAL-2026-Q1 |
| 223 | 2026-01-28 02:03:01 | system | M. Dubois | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PRJ-CORAL-2026-Q1 |
| 224 | 2026-01-28 02:03:02 | system | M. Dubois | notification_logged | CheckInstance:CHK-DATA-RETENTION-PRJ-CORAL-2026-Q1 |
| 225 | 2026-01-28 02:03:03 | system | M. Dubois | check_instance_created | CheckInstance:CHK-DPIA-PRJ-CORAL-2026 |
| 226 | 2026-01-28 02:03:04 | system | M. Dubois | notification_logged | CheckInstance:CHK-DPIA-PRJ-CORAL-2026 |
| 227 | 2026-01-28 02:03:05 | system | M. Dubois | check_instance_created | CheckInstance:CHK-TRAINING-PRJ-CORAL-2026-Q1 |
| 228 | 2026-01-28 02:03:06 | system | M. Dubois | notification_logged | CheckInstance:CHK-TRAINING-PRJ-CORAL-2026-Q1 |
| 229 | 2026-01-28 02:03:07 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-01 |
| 230 | 2026-01-28 02:03:08 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-01 |
| 231 | 2026-01-28 02:03:09 | system | S. Haugen | check_instance_created | CheckInstance:CHK-SUPPLIER-ATTEST-PROC-2026 |
| 232 | 2026-01-28 02:03:10 | system | S. Haugen | notification_logged | CheckInstance:CHK-SUPPLIER-ATTEST-PROC-2026 |
| 233 | 2026-01-28 02:03:11 | system | S. Haugen | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 234 | 2026-01-28 02:03:12 | system | S. Haugen | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 235 | 2026-01-28 02:03:13 | system | S. Haugen | check_instance_created | CheckInstance:CHK-TRAINING-PROC-2026-Q1 |
| 236 | 2026-01-28 02:03:14 | system | S. Haugen | notification_logged | CheckInstance:CHK-TRAINING-PROC-2026-Q1 |
| 237 | 2026-01-28 02:03:15 | system | S. Haugen | check_instance_created | CheckInstance:CHK-VENDOR-DD-PROC-2026 |
| 238 | 2026-01-28 02:03:16 | system | S. Haugen | notification_logged | CheckInstance:CHK-VENDOR-DD-PROC-2026 |
| 239 | 2026-01-28 02:03:17 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-DPIA-MKTG-2026 |
| 240 | 2026-01-28 02:03:18 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-01 |
| 241 | 2026-01-28 02:03:19 | user | user | cycle_completed | Cycle:2026-01-28 |
| 242 | 2026-01-28 03:00:00 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0555 |
| 243 | 2026-01-28 03:00:01 | system | J. Alvarez | assessment_recorded | Assessment:ASM-DPIA-MKTG-2026-1 |
| 244 | 2026-01-28 03:00:02 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0599 |
| 245 | 2026-01-28 03:00:03 | system | C. Brennan | assessment_recorded | Assessment:ASM-INCIDENT-PM-ITSVC-2026-01-1 |
| 246 | 2026-01-28 03:00:04 | system | prescreen | prescreen_completed | Cycle:2026-01-28 |
| 247 | 2026-01-28 05:00:00 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-ASM-DPIA-MKTG-2026-1 |
| 248 | 2026-01-28 05:00:01 | ai | J. Alvarez | finding_raised | Finding:FND-DPIA-MKTG-2026 |
| 249 | 2026-01-28 05:00:02 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-DPIA-MKTG-2026 |
| 250 | 2026-01-28 05:00:03 | system | C. Brennan | flag_raised | Flag:FLG-GAP-ASM-INCIDENT-PM-ITSVC-2026-01-1 |
| 251 | 2026-01-28 05:00:04 | ai | C. Brennan | finding_raised | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 252 | 2026-01-28 05:00:05 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 253 | 2026-01-28 05:00:06 | system | flagging | flagging_completed | Cycle:2026-01-28 |
| 254 | 2026-01-28 05:30:00 | system | follow-up | followup_completed | Cycle:2026-01-28 |
| 255 | 2026-01-28 06:00:00 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0903 |
| 256 | 2026-01-28 06:00:01 | user | J. Alvarez | remediation_submitted | CheckInstance:CHK-DPIA-MKTG-2026 |
| 257 | 2026-01-28 06:00:02 | user | ID-ALVAREZ | finding_progress_recorded | Finding:FND-DPIA-MKTG-2026 |
| 258 | 2026-01-28 06:00:03 | user | J. Alvarez | evidence_round_opened | EvidenceSubmission:SUB-DPIA-MKTG-2026-R1 |
| 259 | 2026-01-28 06:00:04 | system | J. Alvarez | assessment_recorded | Assessment:ASM-DPIA-MKTG-2026-2 |
| 260 | 2026-01-28 06:00:05 | system | J. Alvarez | assessment_superseded | Assessment:ASM-DPIA-MKTG-2026-1 |
| 261 | 2026-01-28 06:00:06 | user | P. Kaur | evidence_round_insufficient | EvidenceSubmission:SUB-DPIA-MKTG-2026-R1 |
| 262 | 2026-01-28 06:00:07 | user | ID-PA-KAUR | evidence_found_insufficient | Finding:FND-DPIA-MKTG-2026 |
| 263 | 2026-01-28 06:00:00 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0915 |
| 264 | 2026-01-28 06:00:01 | user | C. Brennan | remediation_submitted | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-01 |
| 265 | 2026-01-28 06:00:02 | user | ID-BRENNAN | finding_progress_recorded | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 266 | 2026-01-28 06:00:03 | user | C. Brennan | evidence_round_opened | EvidenceSubmission:SUB-INCIDENT-PM-ITSVC-2026-01-R1 |
| 267 | 2026-01-28 06:00:04 | system | C. Brennan | assessment_recorded | Assessment:ASM-INCIDENT-PM-ITSVC-2026-01-2 |
| 268 | 2026-01-28 06:00:05 | system | C. Brennan | assessment_superseded | Assessment:ASM-INCIDENT-PM-ITSVC-2026-01-1 |
| 269 | 2026-01-28 06:00:06 | user | P. Kaur | evidence_round_insufficient | EvidenceSubmission:SUB-INCIDENT-PM-ITSVC-2026-01-R1 |
| 270 | 2026-01-28 06:00:07 | user | ID-PA-KAUR | evidence_found_insufficient | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 271 | 2026-01-28 07:00:00 | ai | S. Haugen | finding_classified | Finding:FND-DOC-2026-09-01 |
| 272 | 2026-01-28 07:00:01 | ai | A. Novak | finding_classified | Finding:FND-DOC-2026-09-02 |
| 273 | 2026-01-28 07:00:02 | ai | C. Brennan | finding_classified | Finding:FND-DOC-2026-09-03 |
| 274 | 2026-01-28 07:00:03 | ai | J. Alvarez | finding_classified | Finding:FND-DPIA-MKTG-2026 |
| 275 | 2026-01-28 07:00:04 | ai | L. Okafor | finding_classified | Finding:FND-IA-2026-H1-01 |
| 276 | 2026-01-28 07:00:05 | ai | R. Mehta | finding_classified | Finding:FND-IA-2026-H1-02 |
| 277 | 2026-01-28 07:00:06 | ai | D. Ferreira | finding_classified | Finding:FND-IA-2026-H1-03 |
| 278 | 2026-01-28 07:00:07 | ai | C. Brennan | finding_classified | Finding:FND-IA-2026-H2-01 |
| 279 | 2026-01-28 07:00:08 | ai | J. Alvarez | finding_classified | Finding:FND-IA-2026-H2-02 |
| 280 | 2026-01-28 07:00:09 | ai | M. Dubois | finding_classified | Finding:FND-IA-2026-H2-03 |
| 281 | 2026-01-28 07:00:10 | ai | C. Brennan | finding_classified | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 282 | 2026-01-28 07:00:11 | ai | N. Iyer | finding_classified | Finding:FND-QA-2026-Q2-01 |
| 283 | 2026-01-28 07:00:12 | ai | E. Vasquez | finding_classified | Finding:FND-QA-2026-Q2-02 |
| 284 | 2026-01-28 07:00:13 | ai | L. Okafor | finding_classified | Finding:FND-QA-2027-Q1-01 |
| 285 | 2026-01-28 07:00:14 | ai | K. Tanaka | finding_classified | Finding:FND-QA-2027-Q1-02 |
| 286 | 2026-01-28 07:00:15 | ai | E. Vasquez | finding_classified | Finding:FND-REL-2026-07-01 |
| 287 | 2026-01-28 07:00:16 | ai | K. Tanaka | finding_classified | Finding:FND-REL-2026-07-02 |
| 288 | 2026-01-28 07:00:17 | ai | M. Dubois | finding_classified | Finding:FND-REL-2027-04-01 |
| 289 | 2026-01-28 07:00:18 | ai | N. Iyer | finding_classified | Finding:FND-REL-2027-04-02 |
| 290 | 2026-01-28 07:30:00 | ai | E. Vasquez | recurrence_examined | Finding:FND-QA-2026-Q2-02 |
| 291 | 2026-01-28 07:30:01 | ai | C. Brennan | recurrence_examined | Finding:FND-IA-2026-H2-01 |
| 292 | 2026-01-28 07:30:02 | ai | J. Alvarez | recurrence_examined | Finding:FND-IA-2026-H2-02 |
| 293 | 2026-01-28 07:30:03 | ai | M. Dubois | recurrence_examined | Finding:FND-IA-2026-H2-03 |
| 294 | 2026-01-28 07:30:04 | ai | L. Okafor | recurrence_examined | Finding:FND-QA-2027-Q1-01 |
| 295 | 2026-01-28 07:30:05 | ai | K. Tanaka | recurrence_examined | Finding:FND-QA-2027-Q1-02 |
| 296 | 2026-01-28 07:30:06 | ai | M. Dubois | recurrence_examined | Finding:FND-REL-2027-04-01 |
| 297 | 2026-01-28 07:30:07 | ai | N. Iyer | recurrence_examined | Finding:FND-REL-2027-04-02 |
| 298 | 2026-02-27 02:00:00 | user | user | cycle_started | Cycle:2026-02-27 |
| 299 | 2026-02-27 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 300 | 2026-02-27 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 301 | 2026-02-27 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-02 |
| 302 | 2026-02-27 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-02 |
| 303 | 2026-02-27 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 304 | 2026-02-27 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 305 | 2026-02-27 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-02 |
| 306 | 2026-02-27 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-02 |
| 307 | 2026-02-27 02:00:09 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-02 |
| 308 | 2026-02-27 02:00:10 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-02 |
| 309 | 2026-02-27 02:00:11 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 310 | 2026-02-27 02:00:12 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 311 | 2026-02-27 02:00:13 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 312 | 2026-02-27 02:00:14 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 313 | 2026-02-27 02:00:15 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-02 |
| 314 | 2026-02-27 02:00:16 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-02 |
| 315 | 2026-02-27 02:00:17 | system | C. Brennan | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-02 |
| 316 | 2026-02-27 02:00:18 | system | C. Brennan | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-02 |
| 317 | 2026-02-27 02:00:19 | system | C. Brennan | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-02 |
| 318 | 2026-02-27 02:00:20 | system | C. Brennan | notification_logged | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-02 |
| 319 | 2026-02-27 02:00:21 | system | C. Brennan | check_instance_created | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-02 |
| 320 | 2026-02-27 02:00:22 | system | C. Brennan | notification_logged | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-02 |
| 321 | 2026-02-27 02:00:23 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 322 | 2026-02-27 02:00:24 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 323 | 2026-02-27 02:00:25 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-02 |
| 324 | 2026-02-27 02:00:26 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-02 |
| 325 | 2026-02-27 02:00:27 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 326 | 2026-02-27 02:00:28 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 327 | 2026-02-27 02:00:29 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-02 |
| 328 | 2026-02-27 02:00:30 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-02 |
| 329 | 2026-02-27 02:00:31 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-02 |
| 330 | 2026-02-27 02:00:32 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-02 |
| 331 | 2026-02-27 02:00:33 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-02 |
| 332 | 2026-02-27 02:00:34 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-02 |
| 333 | 2026-02-27 02:00:35 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-02 |
| 334 | 2026-02-27 02:00:36 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-02 |
| 335 | 2026-02-27 02:00:37 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-02 |
| 336 | 2026-02-27 02:00:38 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-02 |
| 337 | 2026-02-27 02:00:39 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 338 | 2026-02-27 02:00:40 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 339 | 2026-02-27 02:00:41 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-02 |
| 340 | 2026-02-27 02:00:42 | system | E. Vasquez | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-02 |
| 341 | 2026-02-27 02:00:43 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-02 |
| 342 | 2026-02-27 02:00:44 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-02 |
| 343 | 2026-02-27 02:00:45 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 344 | 2026-02-27 02:00:46 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 345 | 2026-02-27 02:00:47 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-02 |
| 346 | 2026-02-27 02:00:48 | system | E. Vasquez | notification_logged | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-02 |
| 347 | 2026-02-27 02:00:49 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 348 | 2026-02-27 02:00:50 | system | K. Tanaka | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 349 | 2026-02-27 02:00:51 | system | M. Dubois | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-02 |
| 350 | 2026-02-27 02:00:52 | system | M. Dubois | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-02 |
| 351 | 2026-02-27 02:00:53 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-02 |
| 352 | 2026-02-27 02:00:54 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-02 |
| 353 | 2026-02-27 02:00:55 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-01 |
| 354 | 2026-02-27 02:00:56 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-01 |
| 355 | 2026-02-27 02:00:57 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-01 |
| 356 | 2026-02-27 02:00:58 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-01 |
| 357 | 2026-02-27 02:00:59 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-01 |
| 358 | 2026-02-27 02:01:00 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-01 |
| 359 | 2026-02-27 02:01:01 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-01 |
| 360 | 2026-02-27 02:01:02 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-01 |
| 361 | 2026-02-27 02:01:03 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-HR-2026-01 |
| 362 | 2026-02-27 02:01:04 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-01 |
| 363 | 2026-02-27 02:01:05 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-01 |
| 364 | 2026-02-27 02:01:06 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 365 | 2026-02-27 02:01:07 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-01 |
| 366 | 2026-02-27 02:01:08 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-01 |
| 367 | 2026-02-27 02:01:09 | user | K. Tanaka | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-01 |
| 368 | 2026-02-27 02:01:10 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-01 |
| 369 | 2026-02-27 02:01:11 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-01 |
| 370 | 2026-02-27 02:01:12 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-01 |
| 371 | 2026-02-27 02:01:13 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-01 |
| 372 | 2026-02-27 02:01:14 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-01 |
| 373 | 2026-02-27 02:01:15 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-01 |
| 374 | 2026-02-27 02:01:16 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 375 | 2026-02-27 02:01:17 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-01 |
| 376 | 2026-02-27 02:01:18 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-01 |
| 377 | 2026-02-27 02:01:19 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-01 |
| 378 | 2026-02-27 02:01:20 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 379 | 2026-02-27 02:01:21 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-01 |
| 380 | 2026-02-27 02:01:22 | user | user | cycle_completed | Cycle:2026-02-27 |
| 381 | 2026-02-27 03:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0083 |
| 382 | 2026-02-27 03:00:01 | system | R. Mehta | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-CUSTOPS-2026-01-1 |
| 383 | 2026-02-27 03:00:02 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0101 |
| 384 | 2026-02-27 03:00:03 | system | A. Novak | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-FINREP-2026-01-1 |
| 385 | 2026-02-27 03:00:04 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0119 |
| 386 | 2026-02-27 03:00:05 | system | C. Brennan | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-ITSVC-2026-01-1 |
| 387 | 2026-02-27 03:00:06 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0136 |
| 388 | 2026-02-27 03:00:07 | system | L. Okafor | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PAYMENTS-2026-01-1 |
| 389 | 2026-02-27 03:00:08 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0154 |
| 390 | 2026-02-27 03:00:09 | system | N. Iyer | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PLATFORM-2026-01-1 |
| 391 | 2026-02-27 03:00:10 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0171 |
| 392 | 2026-02-27 03:00:11 | system | E. Vasquez | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PRJ-ATLAS-2026-01-1 |
| 393 | 2026-02-27 03:00:12 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0200 |
| 394 | 2026-02-27 03:00:13 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0217 |
| 395 | 2026-02-27 03:00:14 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0235 |
| 396 | 2026-02-27 03:00:15 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0253 |
| 397 | 2026-02-27 03:00:16 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0270 |
| 398 | 2026-02-27 03:00:17 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0288 |
| 399 | 2026-02-27 03:00:18 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0306 |
| 400 | 2026-02-27 03:00:19 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0324 |
| 401 | 2026-02-27 03:00:20 | user | K. Tanaka | evidence_bound | Evidence:EV-SUB-0342 |
| 402 | 2026-02-27 03:00:21 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0360 |
| 403 | 2026-02-27 03:00:22 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0378 |
| 404 | 2026-02-27 03:00:23 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0436 |
| 405 | 2026-02-27 03:00:24 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0453 |
| 406 | 2026-02-27 03:00:25 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0471 |
| 407 | 2026-02-27 03:00:26 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0489 |
| 408 | 2026-02-27 03:00:27 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0563 |
| 409 | 2026-02-27 03:00:28 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0581 |
| 410 | 2026-02-27 03:00:29 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0617 |
| 411 | 2026-02-27 03:00:30 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0635 |
| 412 | 2026-02-27 03:00:31 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0653 |
| 413 | 2026-02-27 03:00:32 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0490 |
| 414 | 2026-02-27 03:00:33 | system | E. Vasquez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-1 |
| 415 | 2026-02-27 03:00:34 | system | prescreen | prescreen_completed | Cycle:2026-02-27 |
| 416 | 2026-02-27 04:00:00 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CHANGE-MGMT-CUSTOPS-2026-01-1 |
| 417 | 2026-02-27 04:00:01 | ai | A. Novak | assessment_recorded | Assessment:ASM-CHANGE-MGMT-FINREP-2026-01-1 |
| 418 | 2026-02-27 04:00:02 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-CHANGE-MGMT-HR-2026-01-1 |
| 419 | 2026-02-27 04:00:03 | ai | C. Brennan | assessment_recorded | Assessment:ASM-CHANGE-MGMT-ITSVC-2026-01-1 |
| 420 | 2026-02-27 04:00:04 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-MKTG-2026-01-1 |
| 421 | 2026-02-27 04:00:05 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PAYMENTS-2026-01-1 |
| 422 | 2026-02-27 04:00:06 | ai | N. Iyer | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PLATFORM-2026-01-1 |
| 423 | 2026-02-27 04:00:07 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-ATLAS-2026-01-1 |
| 424 | 2026-02-27 04:00:08 | ai | K. Tanaka | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-BEACON-2026-01-1 |
| 425 | 2026-02-27 04:00:09 | ai | M. Dubois | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-CORAL-2026-01-1 |
| 426 | 2026-02-27 04:00:10 | ai | S. Haugen | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PROC-2026-01-1 |
| 427 | 2026-02-27 04:00:11 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-CUSTOPS-2026-01-1 |
| 428 | 2026-02-27 04:00:12 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-MKTG-2026-01-1 |
| 429 | 2026-02-27 04:00:13 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PAYMENTS-2026-01-1 |
| 430 | 2026-02-27 04:00:14 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-01-1 |
| 431 | 2026-02-27 04:00:15 | ai | R. Mehta | assessment_recorded | Assessment:ASM-INCIDENT-PM-CUSTOPS-2026-01-1 |
| 432 | 2026-02-27 04:00:16 | ai | A. Novak | assessment_recorded | Assessment:ASM-INCIDENT-PM-FINREP-2026-01-1 |
| 433 | 2026-02-27 04:00:17 | ai | L. Okafor | assessment_recorded | Assessment:ASM-INCIDENT-PM-PAYMENTS-2026-01-1 |
| 434 | 2026-02-27 04:00:18 | ai | N. Iyer | assessment_recorded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-01-1 |
| 435 | 2026-02-27 04:00:19 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-INCIDENT-PM-PRJ-ATLAS-2026-01-1 |
| 436 | 2026-02-27 04:00:20 | system | assessor | assessment_completed | Cycle:2026-02-27 |
| 437 | 2026-02-27 05:00:00 | system | E. Vasquez | flag_raised | Flag:FLG-GAP-ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-1 |
| 438 | 2026-02-27 05:00:01 | ai | E. Vasquez | finding_raised | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 439 | 2026-02-27 05:00:02 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 440 | 2026-02-27 05:00:03 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-ASM-DPIA-MKTG-2026-2 |
| 441 | 2026-02-27 05:00:04 | system | C. Brennan | flag_raised | Flag:FLG-GAP-ASM-INCIDENT-PM-ITSVC-2026-01-2 |
| 442 | 2026-02-27 05:00:05 | system | N. Iyer | flag_raised | Flag:FLG-GAP-ASM-INCIDENT-PM-PLATFORM-2026-01-1 |
| 443 | 2026-02-27 05:00:06 | ai | N. Iyer | finding_raised | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 444 | 2026-02-27 05:00:07 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 445 | 2026-02-27 05:00:08 | system | flagging | flagging_completed | Cycle:2026-02-27 |
| 446 | 2026-02-27 05:30:00 | system | J. Alvarez | finding_reminder_sent | Finding:FND-DPIA-MKTG-2026 |
| 447 | 2026-02-27 05:30:01 | system | ID-ALVAREZ | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 448 | 2026-02-27 05:30:02 | system | C. Brennan | finding_reminder_sent | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 449 | 2026-02-27 05:30:03 | system | ID-BRENNAN | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 450 | 2026-02-27 05:30:04 | system | M. Castellanos | finding_escalated | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 451 | 2026-02-27 05:30:05 | system | ID-OPSDIR | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 452 | 2026-02-27 05:30:06 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 453 | 2026-02-27 05:30:07 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 454 | 2026-02-27 05:30:08 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 455 | 2026-02-27 05:30:09 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 456 | 2026-02-27 05:30:10 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 457 | 2026-02-27 05:30:11 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 458 | 2026-02-27 05:30:12 | system | follow-up | followup_completed | Cycle:2026-02-27 |
| 459 | 2026-02-27 06:00:00 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0893 |
| 460 | 2026-02-27 06:00:01 | user | E. Vasquez | remediation_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 461 | 2026-02-27 06:00:02 | user | ID-VASQUEZ | finding_progress_recorded | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 462 | 2026-02-27 06:00:03 | user | E. Vasquez | evidence_round_opened | EvidenceSubmission:SUB-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-R1 |
| 463 | 2026-02-27 06:00:04 | system | E. Vasquez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-2 |
| 464 | 2026-02-27 06:00:05 | system | E. Vasquez | assessment_superseded | Assessment:ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-1 |
| 465 | 2026-02-27 06:00:06 | user | P. Kaur | evidence_round_insufficient | EvidenceSubmission:SUB-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-R1 |
| 466 | 2026-02-27 06:00:07 | user | ID-PA-KAUR | evidence_found_insufficient | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 467 | 2026-02-27 06:00:00 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0904 |
| 468 | 2026-02-27 06:00:01 | user | J. Alvarez | remediation_submitted | CheckInstance:CHK-DPIA-MKTG-2026 |
| 469 | 2026-02-27 06:00:02 | user | ID-ALVAREZ | finding_progress_recorded | Finding:FND-DPIA-MKTG-2026 |
| 470 | 2026-02-27 06:00:03 | user | J. Alvarez | evidence_round_opened | EvidenceSubmission:SUB-DPIA-MKTG-2026-R2 |
| 471 | 2026-02-27 06:00:04 | system | J. Alvarez | assessment_recorded | Assessment:ASM-DPIA-MKTG-2026-3 |
| 472 | 2026-02-27 06:00:05 | system | J. Alvarez | assessment_superseded | Assessment:ASM-DPIA-MKTG-2026-2 |
| 473 | 2026-02-27 06:00:06 | user | P. Kaur | evidence_round_insufficient | EvidenceSubmission:SUB-DPIA-MKTG-2026-R2 |
| 474 | 2026-02-27 06:00:07 | user | ID-PA-KAUR | evidence_found_insufficient | Finding:FND-DPIA-MKTG-2026 |
| 475 | 2026-02-27 07:00:00 | ai | E. Vasquez | finding_classified | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 476 | 2026-02-27 07:00:01 | ai | N. Iyer | finding_classified | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 477 | 2026-02-27 07:30:00 | ai | E. Vasquez | recurrence_examined | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 478 | 2026-02-27 07:30:01 | ai | N. Iyer | recurrence_examined | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 479 | 2026-02-27 07:30:02 | ai | E. Vasquez | recurrence_examined | Finding:FND-QA-2026-Q2-02 |
| 480 | 2026-02-27 07:30:03 | ai | J. Alvarez | recurrence_examined | Finding:FND-IA-2026-H2-02 |
| 481 | 2026-02-27 07:30:04 | ai | K. Tanaka | recurrence_examined | Finding:FND-QA-2027-Q1-02 |
| 482 | 2026-02-27 07:30:05 | ai | M. Dubois | recurrence_examined | Finding:FND-REL-2027-04-01 |
| 483 | 2026-02-27 07:30:06 | ai | N. Iyer | recurrence_examined | Finding:FND-REL-2027-04-02 |
| 484 | 2026-03-29 02:00:00 | user | user | cycle_started | Cycle:2026-03-29 |
| 485 | 2026-03-29 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-03 |
| 486 | 2026-03-29 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-03 |
| 487 | 2026-03-29 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-03 |
| 488 | 2026-03-29 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-03 |
| 489 | 2026-03-29 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 490 | 2026-03-29 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 491 | 2026-03-29 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-03 |
| 492 | 2026-03-29 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-03 |
| 493 | 2026-03-29 02:00:09 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-03 |
| 494 | 2026-03-29 02:00:10 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-03 |
| 495 | 2026-03-29 02:00:11 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-03 |
| 496 | 2026-03-29 02:00:12 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-03 |
| 497 | 2026-03-29 02:00:13 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-03 |
| 498 | 2026-03-29 02:00:14 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-03 |
| 499 | 2026-03-29 02:00:15 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-03 |
| 500 | 2026-03-29 02:00:16 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-03 |
| 501 | 2026-03-29 02:00:17 | system | C. Brennan | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-03 |
| 502 | 2026-03-29 02:00:18 | system | C. Brennan | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-03 |
| 503 | 2026-03-29 02:00:19 | system | C. Brennan | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-03 |
| 504 | 2026-03-29 02:00:20 | system | C. Brennan | notification_logged | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-03 |
| 505 | 2026-03-29 02:00:21 | system | C. Brennan | check_instance_created | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-03 |
| 506 | 2026-03-29 02:00:22 | system | C. Brennan | notification_logged | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-03 |
| 507 | 2026-03-29 02:00:23 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-03 |
| 508 | 2026-03-29 02:00:24 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-03 |
| 509 | 2026-03-29 02:00:25 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-03 |
| 510 | 2026-03-29 02:00:26 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-03 |
| 511 | 2026-03-29 02:00:27 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-03 |
| 512 | 2026-03-29 02:00:28 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-03 |
| 513 | 2026-03-29 02:00:29 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 514 | 2026-03-29 02:00:30 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 515 | 2026-03-29 02:00:31 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-03 |
| 516 | 2026-03-29 02:00:32 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-03 |
| 517 | 2026-03-29 02:00:33 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-03 |
| 518 | 2026-03-29 02:00:34 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-03 |
| 519 | 2026-03-29 02:00:35 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-03 |
| 520 | 2026-03-29 02:00:36 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-03 |
| 521 | 2026-03-29 02:00:37 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-03 |
| 522 | 2026-03-29 02:00:38 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-03 |
| 523 | 2026-03-29 02:00:39 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-03 |
| 524 | 2026-03-29 02:00:40 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-03 |
| 525 | 2026-03-29 02:00:41 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-03 |
| 526 | 2026-03-29 02:00:42 | system | E. Vasquez | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-03 |
| 527 | 2026-03-29 02:00:43 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-03 |
| 528 | 2026-03-29 02:00:44 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-03 |
| 529 | 2026-03-29 02:00:45 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-03 |
| 530 | 2026-03-29 02:00:46 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-03 |
| 531 | 2026-03-29 02:00:47 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-03 |
| 532 | 2026-03-29 02:00:48 | system | E. Vasquez | notification_logged | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-03 |
| 533 | 2026-03-29 02:00:49 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-03 |
| 534 | 2026-03-29 02:00:50 | system | K. Tanaka | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-03 |
| 535 | 2026-03-29 02:00:51 | system | M. Dubois | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-03 |
| 536 | 2026-03-29 02:00:52 | system | M. Dubois | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-03 |
| 537 | 2026-03-29 02:00:53 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-03 |
| 538 | 2026-03-29 02:00:54 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-03 |
| 539 | 2026-03-29 02:00:55 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-02 |
| 540 | 2026-03-29 02:00:56 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-02 |
| 541 | 2026-03-29 02:00:57 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-02 |
| 542 | 2026-03-29 02:00:58 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-02 |
| 543 | 2026-03-29 02:00:59 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-02 |
| 544 | 2026-03-29 02:01:00 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-02 |
| 545 | 2026-03-29 02:01:01 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-02 |
| 546 | 2026-03-29 02:01:02 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 547 | 2026-03-29 02:01:03 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-HR-2026-02 |
| 548 | 2026-03-29 02:01:04 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-02 |
| 549 | 2026-03-29 02:01:05 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 550 | 2026-03-29 02:01:06 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-02 |
| 551 | 2026-03-29 02:01:07 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-02 |
| 552 | 2026-03-29 02:01:08 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-02 |
| 553 | 2026-03-29 02:01:09 | user | K. Tanaka | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 554 | 2026-03-29 02:01:10 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-02 |
| 555 | 2026-03-29 02:01:11 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-02 |
| 556 | 2026-03-29 02:01:12 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-02 |
| 557 | 2026-03-29 02:01:13 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-02 |
| 558 | 2026-03-29 02:01:14 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-02 |
| 559 | 2026-03-29 02:01:15 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-02 |
| 560 | 2026-03-29 02:01:16 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 561 | 2026-03-29 02:01:17 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-02 |
| 562 | 2026-03-29 02:01:18 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-02 |
| 563 | 2026-03-29 02:01:19 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 564 | 2026-03-29 02:01:20 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-02 |
| 565 | 2026-03-29 02:01:21 | user | user | cycle_completed | Cycle:2026-03-29 |
| 566 | 2026-03-29 03:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0084 |
| 567 | 2026-03-29 03:00:01 | system | R. Mehta | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-CUSTOPS-2026-02-1 |
| 568 | 2026-03-29 03:00:02 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0102 |
| 569 | 2026-03-29 03:00:03 | system | A. Novak | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-FINREP-2026-02-1 |
| 570 | 2026-03-29 03:00:04 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0120 |
| 571 | 2026-03-29 03:00:05 | system | C. Brennan | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-ITSVC-2026-02-1 |
| 572 | 2026-03-29 03:00:06 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0137 |
| 573 | 2026-03-29 03:00:07 | system | L. Okafor | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PAYMENTS-2026-02-1 |
| 574 | 2026-03-29 03:00:08 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0155 |
| 575 | 2026-03-29 03:00:09 | system | N. Iyer | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PLATFORM-2026-02-1 |
| 576 | 2026-03-29 03:00:10 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0172 |
| 577 | 2026-03-29 03:00:11 | system | E. Vasquez | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PRJ-ATLAS-2026-02-1 |
| 578 | 2026-03-29 03:00:12 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0201 |
| 579 | 2026-03-29 03:00:13 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0218 |
| 580 | 2026-03-29 03:00:14 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0236 |
| 581 | 2026-03-29 03:00:15 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0254 |
| 582 | 2026-03-29 03:00:16 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0271 |
| 583 | 2026-03-29 03:00:17 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0289 |
| 584 | 2026-03-29 03:00:18 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0307 |
| 585 | 2026-03-29 03:00:19 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0325 |
| 586 | 2026-03-29 03:00:20 | user | K. Tanaka | evidence_bound | Evidence:EV-SUB-0343 |
| 587 | 2026-03-29 03:00:21 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0361 |
| 588 | 2026-03-29 03:00:22 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0379 |
| 589 | 2026-03-29 03:00:23 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0437 |
| 590 | 2026-03-29 03:00:24 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0454 |
| 591 | 2026-03-29 03:00:25 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0472 |
| 592 | 2026-03-29 03:00:26 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0564 |
| 593 | 2026-03-29 03:00:27 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0582 |
| 594 | 2026-03-29 03:00:28 | system | A. Novak | assessment_recorded | Assessment:ASM-INCIDENT-PM-FINREP-2026-02-1 |
| 595 | 2026-03-29 03:00:29 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0600 |
| 596 | 2026-03-29 03:00:30 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0618 |
| 597 | 2026-03-29 03:00:31 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0636 |
| 598 | 2026-03-29 03:00:32 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0654 |
| 599 | 2026-03-29 03:00:33 | system | prescreen | prescreen_completed | Cycle:2026-03-29 |
| 600 | 2026-03-29 04:00:00 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CHANGE-MGMT-CUSTOPS-2026-02-1 |
| 601 | 2026-03-29 04:00:01 | ai | A. Novak | assessment_recorded | Assessment:ASM-CHANGE-MGMT-FINREP-2026-02-1 |
| 602 | 2026-03-29 04:00:02 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-CHANGE-MGMT-HR-2026-02-1 |
| 603 | 2026-03-29 04:00:03 | ai | C. Brennan | assessment_recorded | Assessment:ASM-CHANGE-MGMT-ITSVC-2026-02-1 |
| 604 | 2026-03-29 04:00:04 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-MKTG-2026-02-1 |
| 605 | 2026-03-29 04:00:05 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PAYMENTS-2026-02-1 |
| 606 | 2026-03-29 04:00:06 | ai | N. Iyer | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PLATFORM-2026-02-1 |
| 607 | 2026-03-29 04:00:07 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-ATLAS-2026-02-1 |
| 608 | 2026-03-29 04:00:08 | ai | K. Tanaka | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1 |
| 609 | 2026-03-29 04:00:09 | ai | M. Dubois | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-CORAL-2026-02-1 |
| 610 | 2026-03-29 04:00:10 | ai | S. Haugen | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PROC-2026-02-1 |
| 611 | 2026-03-29 04:00:11 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-CUSTOPS-2026-02-1 |
| 612 | 2026-03-29 04:00:12 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-MKTG-2026-02-1 |
| 613 | 2026-03-29 04:00:13 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PAYMENTS-2026-02-1 |
| 614 | 2026-03-29 04:00:14 | ai | R. Mehta | assessment_recorded | Assessment:ASM-INCIDENT-PM-CUSTOPS-2026-02-1 |
| 615 | 2026-03-29 04:00:15 | ai | C. Brennan | assessment_recorded | Assessment:ASM-INCIDENT-PM-ITSVC-2026-02-1 |
| 616 | 2026-03-29 04:00:16 | ai | L. Okafor | assessment_recorded | Assessment:ASM-INCIDENT-PM-PAYMENTS-2026-02-1 |
| 617 | 2026-03-29 04:00:17 | ai | N. Iyer | assessment_recorded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-02-1 |
| 618 | 2026-03-29 04:00:18 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-INCIDENT-PM-PRJ-ATLAS-2026-02-1 |
| 619 | 2026-03-29 04:00:19 | system | assessor | assessment_completed | Cycle:2026-03-29 |
| 620 | 2026-03-29 05:00:00 | system | A. Novak | flag_raised | Flag:FLG-GAP-ASM-CHANGE-MGMT-FINREP-2026-02-1 |
| 621 | 2026-03-29 05:00:01 | ai | A. Novak | finding_raised | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 622 | 2026-03-29 05:00:02 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 623 | 2026-03-29 05:00:03 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-ASM-CHANGE-MGMT-MKTG-2026-02-1 |
| 624 | 2026-03-29 05:00:04 | ai | J. Alvarez | finding_raised | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 625 | 2026-03-29 05:00:05 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 626 | 2026-03-29 05:00:06 | system | K. Tanaka | flag_raised | Flag:FLG-GAP-ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1 |
| 627 | 2026-03-29 05:00:07 | ai | K. Tanaka | finding_raised | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 628 | 2026-03-29 05:00:08 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 629 | 2026-03-29 05:00:09 | system | E. Vasquez | flag_raised | Flag:FLG-GAP-ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-02-2 |
| 630 | 2026-03-29 05:00:10 | system | J. Alvarez | flag_raised | Flag:FLG-GAP-ASM-DPIA-MKTG-2026-3 |
| 631 | 2026-03-29 05:00:11 | system | A. Novak | flag_raised | Flag:FLG-GAP-ASM-INCIDENT-PM-FINREP-2026-02-1 |
| 632 | 2026-03-29 05:00:12 | ai | A. Novak | finding_raised | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 633 | 2026-03-29 05:00:13 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 634 | 2026-03-29 05:00:14 | system | N. Iyer | flag_raised | Flag:FLG-GAP-ASM-INCIDENT-PM-PLATFORM-2026-02-1 |
| 635 | 2026-03-29 05:00:15 | ai | N. Iyer | finding_raised | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 636 | 2026-03-29 05:00:16 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 637 | 2026-03-29 05:00:17 | system | flagging | flagging_completed | Cycle:2026-03-29 |
| 638 | 2026-03-29 05:30:00 | system | E. Vasquez | finding_reminder_sent | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 639 | 2026-03-29 05:30:01 | system | ID-VASQUEZ | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 640 | 2026-03-29 05:30:02 | system | N. Iyer | finding_escalated | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 641 | 2026-03-29 05:30:03 | system | ID-IYER | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 642 | 2026-03-29 05:30:04 | system | ID-PA-KAUR | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 643 | 2026-03-29 05:30:05 | system | ID-PA-OSEI | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 644 | 2026-03-29 05:30:06 | system | H. Lindqvist | finding_escalated | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 645 | 2026-03-29 05:30:07 | system | ID-DIRECTOR | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 646 | 2026-03-29 05:30:08 | system | ID-PA-KAUR | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 647 | 2026-03-29 05:30:09 | system | ID-PA-OSEI | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 648 | 2026-03-29 05:30:10 | system | J. Alvarez | finding_reminder_sent | Finding:FND-DPIA-MKTG-2026 |
| 649 | 2026-03-29 05:30:11 | system | ID-ALVAREZ | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 650 | 2026-03-29 05:30:12 | system | M. Castellanos | finding_escalated | Finding:FND-DPIA-MKTG-2026 |
| 651 | 2026-03-29 05:30:13 | system | ID-OPSDIR | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 652 | 2026-03-29 05:30:14 | system | ID-PA-KAUR | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 653 | 2026-03-29 05:30:15 | system | ID-PA-OSEI | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 654 | 2026-03-29 05:30:16 | system | H. Lindqvist | finding_escalated | Finding:FND-DPIA-MKTG-2026 |
| 655 | 2026-03-29 05:30:17 | system | ID-DIRECTOR | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 656 | 2026-03-29 05:30:18 | system | ID-PA-KAUR | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 657 | 2026-03-29 05:30:19 | system | ID-PA-OSEI | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 658 | 2026-03-29 05:30:20 | system | C. Brennan | finding_reminder_sent | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 659 | 2026-03-29 05:30:21 | system | ID-BRENNAN | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 660 | 2026-03-29 05:30:22 | system | N. Iyer | finding_reminder_sent | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 661 | 2026-03-29 05:30:23 | system | ID-IYER | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 662 | 2026-03-29 05:30:24 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 663 | 2026-03-29 05:30:25 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 664 | 2026-03-29 05:30:26 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 665 | 2026-03-29 05:30:27 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 666 | 2026-03-29 05:30:28 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 667 | 2026-03-29 05:30:29 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 668 | 2026-03-29 05:30:30 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 669 | 2026-03-29 05:30:31 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 670 | 2026-03-29 05:30:32 | system | follow-up | followup_completed | Cycle:2026-03-29 |
| 671 | 2026-03-29 06:00:00 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0840 |
| 672 | 2026-03-29 06:00:01 | user | A. Novak | remediation_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-02 |
| 673 | 2026-03-29 06:00:02 | user | ID-NOVAK | finding_progress_recorded | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 674 | 2026-03-29 06:00:03 | user | A. Novak | evidence_round_opened | EvidenceSubmission:SUB-CHANGE-MGMT-FINREP-2026-02-R1 |
| 675 | 2026-03-29 06:00:04 | ai | A. Novak | assessment_recorded | Assessment:ASM-CHANGE-MGMT-FINREP-2026-02-2 |
| 676 | 2026-03-29 06:00:05 | system | A. Novak | assessment_superseded | Assessment:ASM-CHANGE-MGMT-FINREP-2026-02-1 |
| 677 | 2026-03-29 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-CHANGE-MGMT-FINREP-2026-02-R1 |
| 678 | 2026-03-29 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 679 | 2026-03-29 06:00:08 | system | A. Novak | flag_closed | Flag:FLG-GAP-ASM-CHANGE-MGMT-FINREP-2026-02-1 |
| 680 | 2026-03-29 06:00:00 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0853 |
| 681 | 2026-03-29 06:00:01 | user | L. Okafor | remediation_submitted | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-01 |
| 682 | 2026-03-29 06:00:02 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PAYMENTS-2026-01-2 |
| 683 | 2026-03-29 06:00:03 | system | L. Okafor | assessment_superseded | Assessment:ASM-CHANGE-MGMT-PAYMENTS-2026-01-1 |
| 684 | 2026-03-29 06:00:00 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0919 |
| 685 | 2026-03-29 06:00:01 | user | N. Iyer | remediation_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-01 |
| 686 | 2026-03-29 06:00:02 | user | ID-IYER | finding_progress_recorded | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 687 | 2026-03-29 06:00:03 | user | N. Iyer | evidence_round_opened | EvidenceSubmission:SUB-INCIDENT-PM-PLATFORM-2026-01-R1 |
| 688 | 2026-03-29 06:00:04 | ai | N. Iyer | assessment_recorded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-01-2 |
| 689 | 2026-03-29 06:00:05 | system | N. Iyer | assessment_superseded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-01-1 |
| 690 | 2026-03-29 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-INCIDENT-PM-PLATFORM-2026-01-R1 |
| 691 | 2026-03-29 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-INCIDENT-PM-PLATFORM-2026-01 |
| 692 | 2026-03-29 06:00:08 | system | N. Iyer | flag_closed | Flag:FLG-GAP-ASM-INCIDENT-PM-PLATFORM-2026-01-1 |
| 693 | 2026-03-29 07:00:00 | ai | A. Novak | finding_classified | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 694 | 2026-03-29 07:00:01 | ai | J. Alvarez | finding_classified | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 695 | 2026-03-29 07:00:02 | ai | K. Tanaka | finding_classified | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 696 | 2026-03-29 07:00:03 | ai | A. Novak | finding_classified | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 697 | 2026-03-29 07:00:04 | ai | N. Iyer | finding_classified | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 698 | 2026-03-29 07:30:00 | ai | A. Novak | recurrence_examined | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 699 | 2026-03-29 07:30:01 | ai | J. Alvarez | recurrence_examined | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 700 | 2026-03-29 07:30:02 | ai | K. Tanaka | recurrence_examined | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 701 | 2026-03-29 07:30:03 | ai | A. Novak | recurrence_examined | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 702 | 2026-03-29 07:30:04 | ai | N. Iyer | recurrence_examined | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 703 | 2026-03-29 07:30:05 | ai | E. Vasquez | recurrence_examined | Finding:FND-QA-2026-Q2-02 |
| 704 | 2026-03-29 07:30:06 | ai | J. Alvarez | recurrence_examined | Finding:FND-IA-2026-H2-02 |
| 705 | 2026-03-29 07:30:07 | ai | K. Tanaka | recurrence_examined | Finding:FND-QA-2027-Q1-02 |
| 706 | 2026-03-29 07:30:08 | ai | M. Dubois | recurrence_examined | Finding:FND-REL-2027-04-01 |
| 707 | 2026-04-28 02:00:00 | user | user | cycle_started | Cycle:2026-04-28 |
| 708 | 2026-04-28 02:00:01 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q2 |
| 709 | 2026-04-28 02:00:02 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q2 |
| 710 | 2026-04-28 02:00:03 | system | R. Mehta | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q2 |
| 711 | 2026-04-28 02:00:04 | system | R. Mehta | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q2 |
| 712 | 2026-04-28 02:00:05 | system | R. Mehta | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-04 |
| 713 | 2026-04-28 02:00:06 | system | R. Mehta | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-04 |
| 714 | 2026-04-28 02:00:07 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-04 |
| 715 | 2026-04-28 02:00:08 | system | R. Mehta | notification_logged | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-04 |
| 716 | 2026-04-28 02:00:09 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q2 |
| 717 | 2026-04-28 02:00:10 | system | R. Mehta | notification_logged | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q2 |
| 718 | 2026-04-28 02:00:11 | system | R. Mehta | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-04 |
| 719 | 2026-04-28 02:00:12 | system | R. Mehta | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-04 |
| 720 | 2026-04-28 02:00:13 | system | R. Mehta | check_instance_created | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q2 |
| 721 | 2026-04-28 02:00:14 | system | R. Mehta | notification_logged | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q2 |
| 722 | 2026-04-28 02:00:15 | system | R. Mehta | check_instance_created | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-04 |
| 723 | 2026-04-28 02:00:16 | system | R. Mehta | notification_logged | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-04 |
| 724 | 2026-04-28 02:00:17 | system | R. Mehta | check_instance_created | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q2 |
| 725 | 2026-04-28 02:00:18 | system | R. Mehta | notification_logged | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q2 |
| 726 | 2026-04-28 02:00:19 | system | A. Novak | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-04 |
| 727 | 2026-04-28 02:00:20 | system | A. Novak | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-04 |
| 728 | 2026-04-28 02:00:21 | system | A. Novak | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-04 |
| 729 | 2026-04-28 02:00:22 | system | A. Novak | notification_logged | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-04 |
| 730 | 2026-04-28 02:00:23 | system | A. Novak | check_instance_created | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-04 |
| 731 | 2026-04-28 02:00:24 | system | A. Novak | notification_logged | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-04 |
| 732 | 2026-04-28 02:00:25 | system | A. Novak | check_instance_created | CheckInstance:CHK-TRAINING-FINREP-2026-Q2 |
| 733 | 2026-04-28 02:00:26 | system | A. Novak | notification_logged | CheckInstance:CHK-TRAINING-FINREP-2026-Q2 |
| 734 | 2026-04-28 02:00:27 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q2 |
| 735 | 2026-04-28 02:00:28 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q2 |
| 736 | 2026-04-28 02:00:29 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q2 |
| 737 | 2026-04-28 02:00:30 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q2 |
| 738 | 2026-04-28 02:00:31 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-HR-2026-04 |
| 739 | 2026-04-28 02:00:32 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CHANGE-MGMT-HR-2026-04 |
| 740 | 2026-04-28 02:00:33 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q2 |
| 741 | 2026-04-28 02:00:34 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q2 |
| 742 | 2026-04-28 02:00:35 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q2 |
| 743 | 2026-04-28 02:00:36 | system | D. Ferreira | notification_logged | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q2 |
| 744 | 2026-04-28 02:00:37 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 745 | 2026-04-28 02:00:38 | system | D. Ferreira | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q2 |
| 746 | 2026-04-28 02:00:39 | system | D. Ferreira | check_instance_created | CheckInstance:CHK-TRAINING-HR-2026-Q2 |
| 747 | 2026-04-28 02:00:40 | system | D. Ferreira | notification_logged | CheckInstance:CHK-TRAINING-HR-2026-Q2 |
| 748 | 2026-04-28 02:00:41 | system | C. Brennan | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-ITSVC-2026-Q2 |
| 749 | 2026-04-28 02:00:42 | system | C. Brennan | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-ITSVC-2026-Q2 |
| 750 | 2026-04-28 02:00:43 | system | C. Brennan | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-ITSVC-2026-Q2 |
| 751 | 2026-04-28 02:00:44 | system | C. Brennan | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-ITSVC-2026-Q2 |
| 752 | 2026-04-28 02:00:45 | system | C. Brennan | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-04 |
| 753 | 2026-04-28 02:00:46 | system | C. Brennan | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-04 |
| 754 | 2026-04-28 02:00:47 | system | C. Brennan | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-04 |
| 755 | 2026-04-28 02:00:48 | system | C. Brennan | notification_logged | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-04 |
| 756 | 2026-04-28 02:00:49 | system | C. Brennan | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-ITSVC-2026-Q2 |
| 757 | 2026-04-28 02:00:50 | system | C. Brennan | notification_logged | CheckInstance:CHK-CRYPTO-KEY-ITSVC-2026-Q2 |
| 758 | 2026-04-28 02:00:51 | system | C. Brennan | check_instance_created | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q2 |
| 759 | 2026-04-28 02:00:52 | system | C. Brennan | notification_logged | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q2 |
| 760 | 2026-04-28 02:00:53 | system | C. Brennan | check_instance_created | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-04 |
| 761 | 2026-04-28 02:00:54 | system | C. Brennan | notification_logged | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-04 |
| 762 | 2026-04-28 02:00:55 | system | C. Brennan | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-ITSVC-2026-Q2 |
| 763 | 2026-04-28 02:00:56 | system | C. Brennan | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-ITSVC-2026-Q2 |
| 764 | 2026-04-28 02:00:57 | system | C. Brennan | check_instance_created | CheckInstance:CHK-TRAINING-ITSVC-2026-Q2 |
| 765 | 2026-04-28 02:00:58 | system | C. Brennan | notification_logged | CheckInstance:CHK-TRAINING-ITSVC-2026-Q2 |
| 766 | 2026-04-28 02:00:59 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q2 |
| 767 | 2026-04-28 02:01:00 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q2 |
| 768 | 2026-04-28 02:01:01 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q2 |
| 769 | 2026-04-28 02:01:02 | system | J. Alvarez | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q2 |
| 770 | 2026-04-28 02:01:03 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-04 |
| 771 | 2026-04-28 02:01:04 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-04 |
| 772 | 2026-04-28 02:01:05 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q2 |
| 773 | 2026-04-28 02:01:06 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q2 |
| 774 | 2026-04-28 02:01:07 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-04 |
| 775 | 2026-04-28 02:01:08 | system | J. Alvarez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-04 |
| 776 | 2026-04-28 02:01:09 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q2 |
| 777 | 2026-04-28 02:01:10 | system | J. Alvarez | notification_logged | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q2 |
| 778 | 2026-04-28 02:01:11 | system | J. Alvarez | check_instance_created | CheckInstance:CHK-TRAINING-MKTG-2026-Q2 |
| 779 | 2026-04-28 02:01:12 | system | J. Alvarez | notification_logged | CheckInstance:CHK-TRAINING-MKTG-2026-Q2 |
| 780 | 2026-04-28 02:01:13 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q2 |
| 781 | 2026-04-28 02:01:14 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q2 |
| 782 | 2026-04-28 02:01:15 | system | L. Okafor | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q2 |
| 783 | 2026-04-28 02:01:16 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q2 |
| 784 | 2026-04-28 02:01:17 | system | L. Okafor | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-04 |
| 785 | 2026-04-28 02:01:18 | system | L. Okafor | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-04 |
| 786 | 2026-04-28 02:01:19 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-04 |
| 787 | 2026-04-28 02:01:20 | system | L. Okafor | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-04 |
| 788 | 2026-04-28 02:01:21 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q2 |
| 789 | 2026-04-28 02:01:22 | system | L. Okafor | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q2 |
| 790 | 2026-04-28 02:01:23 | system | L. Okafor | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-04 |
| 791 | 2026-04-28 02:01:24 | system | L. Okafor | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-04 |
| 792 | 2026-04-28 02:01:25 | system | L. Okafor | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q2 |
| 793 | 2026-04-28 02:01:26 | system | L. Okafor | notification_logged | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q2 |
| 794 | 2026-04-28 02:01:27 | system | L. Okafor | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-04 |
| 795 | 2026-04-28 02:01:28 | system | L. Okafor | notification_logged | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-04 |
| 796 | 2026-04-28 02:01:29 | system | L. Okafor | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q2 |
| 797 | 2026-04-28 02:01:30 | system | L. Okafor | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q2 |
| 798 | 2026-04-28 02:01:31 | system | L. Okafor | check_instance_created | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q2 |
| 799 | 2026-04-28 02:01:32 | system | L. Okafor | notification_logged | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q2 |
| 800 | 2026-04-28 02:01:33 | system | N. Iyer | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-04 |
| 801 | 2026-04-28 02:01:34 | system | N. Iyer | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-04 |
| 802 | 2026-04-28 02:01:35 | system | N. Iyer | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-04 |
| 803 | 2026-04-28 02:01:36 | system | N. Iyer | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-04 |
| 804 | 2026-04-28 02:01:37 | system | N. Iyer | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-04 |
| 805 | 2026-04-28 02:01:38 | system | N. Iyer | notification_logged | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-04 |
| 806 | 2026-04-28 02:01:39 | system | N. Iyer | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q2 |
| 807 | 2026-04-28 02:01:40 | system | N. Iyer | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q2 |
| 808 | 2026-04-28 02:01:41 | system | N. Iyer | check_instance_created | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q2 |
| 809 | 2026-04-28 02:01:42 | system | N. Iyer | notification_logged | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q2 |
| 810 | 2026-04-28 02:01:43 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PRJ-ATLAS-2026-Q2 |
| 811 | 2026-04-28 02:01:44 | system | E. Vasquez | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PRJ-ATLAS-2026-Q2 |
| 812 | 2026-04-28 02:01:45 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PRJ-ATLAS-2026-Q2 |
| 813 | 2026-04-28 02:01:46 | system | E. Vasquez | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PRJ-ATLAS-2026-Q2 |
| 814 | 2026-04-28 02:01:47 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-04 |
| 815 | 2026-04-28 02:01:48 | system | E. Vasquez | notification_logged | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-04 |
| 816 | 2026-04-28 02:01:49 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-04 |
| 817 | 2026-04-28 02:01:50 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-04 |
| 818 | 2026-04-28 02:01:51 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PRJ-ATLAS-2026-Q2 |
| 819 | 2026-04-28 02:01:52 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PRJ-ATLAS-2026-Q2 |
| 820 | 2026-04-28 02:01:53 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-04 |
| 821 | 2026-04-28 02:01:54 | system | E. Vasquez | notification_logged | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-04 |
| 822 | 2026-04-28 02:01:55 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PRJ-ATLAS-2026-Q2 |
| 823 | 2026-04-28 02:01:56 | system | E. Vasquez | notification_logged | CheckInstance:CHK-DATA-RETENTION-PRJ-ATLAS-2026-Q2 |
| 824 | 2026-04-28 02:01:57 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 825 | 2026-04-28 02:01:58 | system | E. Vasquez | notification_logged | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 826 | 2026-04-28 02:01:59 | system | E. Vasquez | check_instance_created | CheckInstance:CHK-TRAINING-PRJ-ATLAS-2026-Q2 |
| 827 | 2026-04-28 02:02:00 | system | E. Vasquez | notification_logged | CheckInstance:CHK-TRAINING-PRJ-ATLAS-2026-Q2 |
| 828 | 2026-04-28 02:02:01 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-04 |
| 829 | 2026-04-28 02:02:02 | system | K. Tanaka | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-04 |
| 830 | 2026-04-28 02:02:03 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q2 |
| 831 | 2026-04-28 02:02:04 | system | K. Tanaka | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q2 |
| 832 | 2026-04-28 02:02:05 | system | K. Tanaka | check_instance_created | CheckInstance:CHK-TRAINING-PRJ-BEACON-2026-Q2 |
| 833 | 2026-04-28 02:02:06 | system | K. Tanaka | notification_logged | CheckInstance:CHK-TRAINING-PRJ-BEACON-2026-Q2 |
| 834 | 2026-04-28 02:02:07 | system | M. Dubois | check_instance_created | CheckInstance:CHK-ACCESS-EXPORT-PRJ-CORAL-2026-Q2 |
| 835 | 2026-04-28 02:02:08 | system | M. Dubois | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PRJ-CORAL-2026-Q2 |
| 836 | 2026-04-28 02:02:09 | system | M. Dubois | check_instance_created | CheckInstance:CHK-ACCESS-REVIEW-PRJ-CORAL-2026-Q2 |
| 837 | 2026-04-28 02:02:10 | system | M. Dubois | notification_logged | CheckInstance:CHK-ACCESS-REVIEW-PRJ-CORAL-2026-Q2 |
| 838 | 2026-04-28 02:02:11 | system | M. Dubois | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-04 |
| 839 | 2026-04-28 02:02:12 | system | M. Dubois | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-04 |
| 840 | 2026-04-28 02:02:13 | system | M. Dubois | check_instance_created | CheckInstance:CHK-CRYPTO-KEY-PRJ-CORAL-2026-Q2 |
| 841 | 2026-04-28 02:02:14 | system | M. Dubois | notification_logged | CheckInstance:CHK-CRYPTO-KEY-PRJ-CORAL-2026-Q2 |
| 842 | 2026-04-28 02:02:15 | system | M. Dubois | check_instance_created | CheckInstance:CHK-DATA-RETENTION-PRJ-CORAL-2026-Q2 |
| 843 | 2026-04-28 02:02:16 | system | M. Dubois | notification_logged | CheckInstance:CHK-DATA-RETENTION-PRJ-CORAL-2026-Q2 |
| 844 | 2026-04-28 02:02:17 | system | M. Dubois | check_instance_created | CheckInstance:CHK-TRAINING-PRJ-CORAL-2026-Q2 |
| 845 | 2026-04-28 02:02:18 | system | M. Dubois | notification_logged | CheckInstance:CHK-TRAINING-PRJ-CORAL-2026-Q2 |
| 846 | 2026-04-28 02:02:19 | system | S. Haugen | check_instance_created | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-04 |
| 847 | 2026-04-28 02:02:20 | system | S. Haugen | notification_logged | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-04 |
| 848 | 2026-04-28 02:02:21 | system | S. Haugen | check_instance_created | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 849 | 2026-04-28 02:02:22 | system | S. Haugen | notification_logged | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q2 |
| 850 | 2026-04-28 02:02:23 | system | S. Haugen | check_instance_created | CheckInstance:CHK-TRAINING-PROC-2026-Q2 |
| 851 | 2026-04-28 02:02:24 | system | S. Haugen | notification_logged | CheckInstance:CHK-TRAINING-PROC-2026-Q2 |
| 852 | 2026-04-28 02:02:25 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-CUSTOPS-2026-Q1 |
| 853 | 2026-04-28 02:02:26 | system | D. Ferreira | check_instance_overdue | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 854 | 2026-04-28 02:02:27 | system | D. Ferreira | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-HR-2026-Q1 |
| 855 | 2026-04-28 02:02:28 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-ITSVC-2026-Q1 |
| 856 | 2026-04-28 02:02:29 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-MKTG-2026-Q1 |
| 857 | 2026-04-28 02:02:30 | system | L. Okafor | check_instance_overdue | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 858 | 2026-04-28 02:02:31 | system | L. Okafor | notification_logged | CheckInstance:CHK-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 859 | 2026-04-28 02:02:32 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-PRJ-ATLAS-2026-Q1 |
| 860 | 2026-04-28 02:02:33 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-ACCESS-EXPORT-PRJ-CORAL-2026-Q1 |
| 861 | 2026-04-28 02:02:34 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 862 | 2026-04-28 02:02:35 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-HR-2026-Q1 |
| 863 | 2026-04-28 02:02:36 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-ITSVC-2026-Q1 |
| 864 | 2026-04-28 02:02:37 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-MKTG-2026-Q1 |
| 865 | 2026-04-28 02:02:38 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-PAYMENTS-2026-Q1 |
| 866 | 2026-04-28 02:02:39 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-PRJ-ATLAS-2026-Q1 |
| 867 | 2026-04-28 02:02:40 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-ACCESS-REVIEW-PRJ-CORAL-2026-Q1 |
| 868 | 2026-04-28 02:02:41 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-CUSTOPS-2026-03 |
| 869 | 2026-04-28 02:02:42 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-FINREP-2026-03 |
| 870 | 2026-04-28 02:02:43 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-ITSVC-2026-03 |
| 871 | 2026-04-28 02:02:44 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PAYMENTS-2026-03 |
| 872 | 2026-04-28 02:02:45 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PLATFORM-2026-03 |
| 873 | 2026-04-28 02:02:46 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-BACKUP-VERIFY-PRJ-ATLAS-2026-03 |
| 874 | 2026-04-28 02:02:47 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-CUSTOPS-2026-03 |
| 875 | 2026-04-28 02:02:48 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-FINREP-2026-03 |
| 876 | 2026-04-28 02:02:49 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-HR-2026-03 |
| 877 | 2026-04-28 02:02:50 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-ITSVC-2026-03 |
| 878 | 2026-04-28 02:02:51 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-03 |
| 879 | 2026-04-28 02:02:52 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PAYMENTS-2026-03 |
| 880 | 2026-04-28 02:02:53 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PLATFORM-2026-03 |
| 881 | 2026-04-28 02:02:54 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-ATLAS-2026-03 |
| 882 | 2026-04-28 02:02:55 | user | K. Tanaka | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-03 |
| 883 | 2026-04-28 02:02:56 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-CORAL-2026-03 |
| 884 | 2026-04-28 02:02:57 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-CHANGE-MGMT-PROC-2026-03 |
| 885 | 2026-04-28 02:02:58 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-CUSTOPS-2026-Q1 |
| 886 | 2026-04-28 02:02:59 | system | D. Ferreira | check_instance_overdue | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 887 | 2026-04-28 02:03:00 | system | D. Ferreira | notification_logged | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 888 | 2026-04-28 02:03:01 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-ITSVC-2026-Q1 |
| 889 | 2026-04-28 02:03:02 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-MKTG-2026-Q1 |
| 890 | 2026-04-28 02:03:03 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-PAYMENTS-2026-Q1 |
| 891 | 2026-04-28 02:03:04 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-PRJ-ATLAS-2026-Q1 |
| 892 | 2026-04-28 02:03:05 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-CRYPTO-KEY-PRJ-CORAL-2026-Q1 |
| 893 | 2026-04-28 02:03:06 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-CUSTOPS-2026-03 |
| 894 | 2026-04-28 02:03:07 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-MKTG-2026-03 |
| 895 | 2026-04-28 02:03:08 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PAYMENTS-2026-03 |
| 896 | 2026-04-28 02:03:09 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-CUST-COMPLAINTS-PRJ-ATLAS-2026-03 |
| 897 | 2026-04-28 02:03:10 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 898 | 2026-04-28 02:03:11 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-HR-2026-Q1 |
| 899 | 2026-04-28 02:03:12 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q1 |
| 900 | 2026-04-28 02:03:13 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q2 |
| 901 | 2026-04-28 02:03:14 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-MKTG-2026-Q1 |
| 902 | 2026-04-28 02:03:15 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-PAYMENTS-2026-Q1 |
| 903 | 2026-04-28 02:03:16 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-PRJ-ATLAS-2026-Q1 |
| 904 | 2026-04-28 02:03:17 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-DATA-RETENTION-PRJ-CORAL-2026-Q1 |
| 905 | 2026-04-28 02:03:18 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-CUSTOPS-2026-03 |
| 906 | 2026-04-28 02:03:19 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-03 |
| 907 | 2026-04-28 02:03:20 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-ITSVC-2026-03 |
| 908 | 2026-04-28 02:03:21 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PAYMENTS-2026-03 |
| 909 | 2026-04-28 02:03:22 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-03 |
| 910 | 2026-04-28 02:03:23 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-03 |
| 911 | 2026-04-28 02:03:24 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 912 | 2026-04-28 02:03:25 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-HR-2026-Q1 |
| 913 | 2026-04-28 02:03:26 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-ITSVC-2026-Q1 |
| 914 | 2026-04-28 02:03:27 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1 |
| 915 | 2026-04-28 02:03:28 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 916 | 2026-04-28 02:03:29 | user | K. Tanaka | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q1 |
| 917 | 2026-04-28 02:03:30 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-THIRD-PARTY-ACCESS-PROC-2026-Q1 |
| 918 | 2026-04-28 02:03:31 | user | R. Mehta | check_instance_submitted | CheckInstance:CHK-TRAINING-CUSTOPS-2026-Q1 |
| 919 | 2026-04-28 02:03:32 | user | A. Novak | check_instance_submitted | CheckInstance:CHK-TRAINING-FINREP-2026-Q1 |
| 920 | 2026-04-28 02:03:33 | user | D. Ferreira | check_instance_submitted | CheckInstance:CHK-TRAINING-HR-2026-Q1 |
| 921 | 2026-04-28 02:03:34 | user | C. Brennan | check_instance_submitted | CheckInstance:CHK-TRAINING-ITSVC-2026-Q1 |
| 922 | 2026-04-28 02:03:35 | user | J. Alvarez | check_instance_submitted | CheckInstance:CHK-TRAINING-MKTG-2026-Q1 |
| 923 | 2026-04-28 02:03:36 | user | L. Okafor | check_instance_submitted | CheckInstance:CHK-TRAINING-PAYMENTS-2026-Q1 |
| 924 | 2026-04-28 02:03:37 | user | N. Iyer | check_instance_submitted | CheckInstance:CHK-TRAINING-PLATFORM-2026-Q1 |
| 925 | 2026-04-28 02:03:38 | user | E. Vasquez | check_instance_submitted | CheckInstance:CHK-TRAINING-PRJ-ATLAS-2026-Q1 |
| 926 | 2026-04-28 02:03:39 | user | K. Tanaka | check_instance_submitted | CheckInstance:CHK-TRAINING-PRJ-BEACON-2026-Q1 |
| 927 | 2026-04-28 02:03:40 | user | M. Dubois | check_instance_submitted | CheckInstance:CHK-TRAINING-PRJ-CORAL-2026-Q1 |
| 928 | 2026-04-28 02:03:41 | user | S. Haugen | check_instance_submitted | CheckInstance:CHK-TRAINING-PROC-2026-Q1 |
| 929 | 2026-04-28 02:03:42 | user | user | cycle_completed | Cycle:2026-04-28 |
| 930 | 2026-04-28 03:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0085 |
| 931 | 2026-04-28 03:00:01 | system | R. Mehta | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-CUSTOPS-2026-03-1 |
| 932 | 2026-04-28 03:00:02 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0103 |
| 933 | 2026-04-28 03:00:03 | system | A. Novak | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-FINREP-2026-03-1 |
| 934 | 2026-04-28 03:00:04 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0121 |
| 935 | 2026-04-28 03:00:05 | system | C. Brennan | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-ITSVC-2026-03-1 |
| 936 | 2026-04-28 03:00:06 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0138 |
| 937 | 2026-04-28 03:00:07 | system | L. Okafor | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PAYMENTS-2026-03-1 |
| 938 | 2026-04-28 03:00:08 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0156 |
| 939 | 2026-04-28 03:00:09 | system | N. Iyer | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PLATFORM-2026-03-1 |
| 940 | 2026-04-28 03:00:10 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0173 |
| 941 | 2026-04-28 03:00:11 | system | E. Vasquez | assessment_recorded | Assessment:ASM-BACKUP-VERIFY-PRJ-ATLAS-2026-03-1 |
| 942 | 2026-04-28 03:00:12 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0202 |
| 943 | 2026-04-28 03:00:13 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0219 |
| 944 | 2026-04-28 03:00:14 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0237 |
| 945 | 2026-04-28 03:00:15 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0255 |
| 946 | 2026-04-28 03:00:16 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0272 |
| 947 | 2026-04-28 03:00:17 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0290 |
| 948 | 2026-04-28 03:00:18 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0308 |
| 949 | 2026-04-28 03:00:19 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0326 |
| 950 | 2026-04-28 03:00:20 | user | K. Tanaka | evidence_bound | Evidence:EV-SUB-0344 |
| 951 | 2026-04-28 03:00:21 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0362 |
| 952 | 2026-04-28 03:00:22 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0380 |
| 953 | 2026-04-28 03:00:23 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0438 |
| 954 | 2026-04-28 03:00:24 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0455 |
| 955 | 2026-04-28 03:00:25 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0473 |
| 956 | 2026-04-28 03:00:26 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0491 |
| 957 | 2026-04-28 03:00:27 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0565 |
| 958 | 2026-04-28 03:00:28 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0583 |
| 959 | 2026-04-28 03:00:29 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0601 |
| 960 | 2026-04-28 03:00:30 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0619 |
| 961 | 2026-04-28 03:00:31 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0637 |
| 962 | 2026-04-28 03:00:32 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0655 |
| 963 | 2026-04-28 03:00:33 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0656 |
| 964 | 2026-04-28 03:00:34 | system | E. Vasquez | assessment_recorded | Assessment:ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-1 |
| 965 | 2026-04-28 03:00:35 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0001 |
| 966 | 2026-04-28 03:00:36 | system | R. Mehta | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-CUSTOPS-2026-Q1-1 |
| 967 | 2026-04-28 03:00:37 | system | D. Ferreira | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-HR-2026-Q1-1 |
| 968 | 2026-04-28 03:00:38 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0012 |
| 969 | 2026-04-28 03:00:39 | system | C. Brennan | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-ITSVC-2026-Q1-1 |
| 970 | 2026-04-28 03:00:40 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0018 |
| 971 | 2026-04-28 03:00:41 | system | J. Alvarez | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-MKTG-2026-Q1-1 |
| 972 | 2026-04-28 03:00:42 | system | L. Okafor | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-PAYMENTS-2026-Q1-1 |
| 973 | 2026-04-28 03:00:43 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0029 |
| 974 | 2026-04-28 03:00:44 | system | E. Vasquez | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-PRJ-ATLAS-2026-Q1-1 |
| 975 | 2026-04-28 03:00:45 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0035 |
| 976 | 2026-04-28 03:00:46 | system | M. Dubois | assessment_recorded | Assessment:ASM-ACCESS-EXPORT-PRJ-CORAL-2026-Q1-1 |
| 977 | 2026-04-28 03:00:47 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0041 |
| 978 | 2026-04-28 03:00:48 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0047 |
| 979 | 2026-04-28 03:00:49 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0053 |
| 980 | 2026-04-28 03:00:50 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0059 |
| 981 | 2026-04-28 03:00:51 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0065 |
| 982 | 2026-04-28 03:00:52 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0071 |
| 983 | 2026-04-28 03:00:53 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0077 |
| 984 | 2026-04-28 03:00:54 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0396 |
| 985 | 2026-04-28 03:00:55 | system | D. Ferreira | assessment_recorded | Assessment:ASM-CRYPTO-KEY-HR-2026-Q1-1 |
| 986 | 2026-04-28 03:00:56 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0407 |
| 987 | 2026-04-28 03:00:57 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0413 |
| 988 | 2026-04-28 03:00:58 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0419 |
| 989 | 2026-04-28 03:00:59 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0424 |
| 990 | 2026-04-28 03:01:00 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0430 |
| 991 | 2026-04-28 03:01:01 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0507 |
| 992 | 2026-04-28 03:01:02 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0513 |
| 993 | 2026-04-28 03:01:03 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0519 |
| 994 | 2026-04-28 03:01:04 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0525 |
| 995 | 2026-04-28 03:01:05 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0531 |
| 996 | 2026-04-28 03:01:06 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0537 |
| 997 | 2026-04-28 03:01:07 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0543 |
| 998 | 2026-04-28 03:01:08 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0684 |
| 999 | 2026-04-28 03:01:09 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0690 |
| 1000 | 2026-04-28 03:01:10 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0700 |
| 1001 | 2026-04-28 03:01:11 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0706 |
| 1002 | 2026-04-28 03:01:12 | user | K. Tanaka | evidence_bound | Evidence:EV-SUB-0712 |
| 1003 | 2026-04-28 03:01:13 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0718 |
| 1004 | 2026-04-28 03:01:14 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0724 |
| 1005 | 2026-04-28 03:01:15 | system | R. Mehta | assessment_recorded | Assessment:ASM-TRAINING-CUSTOPS-2026-Q1-1 |
| 1006 | 2026-04-28 03:01:16 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0730 |
| 1007 | 2026-04-28 03:01:17 | system | A. Novak | assessment_recorded | Assessment:ASM-TRAINING-FINREP-2026-Q1-1 |
| 1008 | 2026-04-28 03:01:18 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-0736 |
| 1009 | 2026-04-28 03:01:19 | system | D. Ferreira | assessment_recorded | Assessment:ASM-TRAINING-HR-2026-Q1-1 |
| 1010 | 2026-04-28 03:01:20 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0742 |
| 1011 | 2026-04-28 03:01:21 | system | C. Brennan | assessment_recorded | Assessment:ASM-TRAINING-ITSVC-2026-Q1-1 |
| 1012 | 2026-04-28 03:01:22 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0748 |
| 1013 | 2026-04-28 03:01:23 | system | J. Alvarez | assessment_recorded | Assessment:ASM-TRAINING-MKTG-2026-Q1-1 |
| 1014 | 2026-04-28 03:01:24 | user | L. Okafor | evidence_bound | Evidence:EV-SUB-0754 |
| 1015 | 2026-04-28 03:01:25 | system | L. Okafor | assessment_recorded | Assessment:ASM-TRAINING-PAYMENTS-2026-Q1-1 |
| 1016 | 2026-04-28 03:01:26 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0760 |
| 1017 | 2026-04-28 03:01:27 | system | N. Iyer | assessment_recorded | Assessment:ASM-TRAINING-PLATFORM-2026-Q1-1 |
| 1018 | 2026-04-28 03:01:28 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0766 |
| 1019 | 2026-04-28 03:01:29 | system | E. Vasquez | assessment_recorded | Assessment:ASM-TRAINING-PRJ-ATLAS-2026-Q1-1 |
| 1020 | 2026-04-28 03:01:30 | user | K. Tanaka | evidence_bound | Evidence:EV-SUB-0772 |
| 1021 | 2026-04-28 03:01:31 | system | K. Tanaka | assessment_recorded | Assessment:ASM-TRAINING-PRJ-BEACON-2026-Q1-1 |
| 1022 | 2026-04-28 03:01:32 | user | M. Dubois | evidence_bound | Evidence:EV-SUB-0778 |
| 1023 | 2026-04-28 03:01:33 | system | M. Dubois | assessment_recorded | Assessment:ASM-TRAINING-PRJ-CORAL-2026-Q1-1 |
| 1024 | 2026-04-28 03:01:34 | user | S. Haugen | evidence_bound | Evidence:EV-SUB-0784 |
| 1025 | 2026-04-28 03:01:35 | system | S. Haugen | assessment_recorded | Assessment:ASM-TRAINING-PROC-2026-Q1-1 |
| 1026 | 2026-04-28 03:01:36 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0520 |
| 1027 | 2026-04-28 03:01:37 | system | C. Brennan | assessment_recorded | Assessment:ASM-DATA-RETENTION-ITSVC-2026-Q2-1 |
| 1028 | 2026-04-28 03:01:38 | system | prescreen | prescreen_completed | Cycle:2026-04-28 |
| 1029 | 2026-04-28 04:00:00 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CHANGE-MGMT-CUSTOPS-2026-03-1 |
| 1030 | 2026-04-28 04:00:01 | ai | A. Novak | assessment_recorded | Assessment:ASM-CHANGE-MGMT-FINREP-2026-03-1 |
| 1031 | 2026-04-28 04:00:02 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-CHANGE-MGMT-HR-2026-03-1 |
| 1032 | 2026-04-28 04:00:03 | ai | C. Brennan | assessment_recorded | Assessment:ASM-CHANGE-MGMT-ITSVC-2026-03-1 |
| 1033 | 2026-04-28 04:00:04 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-MKTG-2026-03-1 |
| 1034 | 2026-04-28 04:00:05 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PAYMENTS-2026-03-1 |
| 1035 | 2026-04-28 04:00:06 | ai | N. Iyer | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PLATFORM-2026-03-1 |
| 1036 | 2026-04-28 04:00:07 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-ATLAS-2026-03-1 |
| 1037 | 2026-04-28 04:00:08 | ai | K. Tanaka | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-BEACON-2026-03-1 |
| 1038 | 2026-04-28 04:00:09 | ai | M. Dubois | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-CORAL-2026-03-1 |
| 1039 | 2026-04-28 04:00:10 | ai | S. Haugen | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PROC-2026-03-1 |
| 1040 | 2026-04-28 04:00:11 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-CUSTOPS-2026-03-1 |
| 1041 | 2026-04-28 04:00:12 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-MKTG-2026-03-1 |
| 1042 | 2026-04-28 04:00:13 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PAYMENTS-2026-03-1 |
| 1043 | 2026-04-28 04:00:14 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-CUST-COMPLAINTS-PRJ-ATLAS-2026-03-1 |
| 1044 | 2026-04-28 04:00:15 | ai | R. Mehta | assessment_recorded | Assessment:ASM-INCIDENT-PM-CUSTOPS-2026-03-1 |
| 1045 | 2026-04-28 04:00:16 | ai | A. Novak | assessment_recorded | Assessment:ASM-INCIDENT-PM-FINREP-2026-03-1 |
| 1046 | 2026-04-28 04:00:17 | ai | C. Brennan | assessment_recorded | Assessment:ASM-INCIDENT-PM-ITSVC-2026-03-1 |
| 1047 | 2026-04-28 04:00:18 | ai | L. Okafor | assessment_recorded | Assessment:ASM-INCIDENT-PM-PAYMENTS-2026-03-1 |
| 1048 | 2026-04-28 04:00:19 | ai | N. Iyer | assessment_recorded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-03-1 |
| 1049 | 2026-04-28 04:00:20 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-INCIDENT-PM-PRJ-ATLAS-2026-03-1 |
| 1050 | 2026-04-28 04:00:21 | ai | R. Mehta | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 1051 | 2026-04-28 04:00:22 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-HR-2026-Q1-1 |
| 1052 | 2026-04-28 04:00:23 | ai | C. Brennan | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-ITSVC-2026-Q1-1 |
| 1053 | 2026-04-28 04:00:24 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-MKTG-2026-Q1-1 |
| 1054 | 2026-04-28 04:00:25 | ai | L. Okafor | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-PAYMENTS-2026-Q1-1 |
| 1055 | 2026-04-28 04:00:26 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-PRJ-ATLAS-2026-Q1-1 |
| 1056 | 2026-04-28 04:00:27 | ai | M. Dubois | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-PRJ-CORAL-2026-Q1-1 |
| 1057 | 2026-04-28 04:00:28 | ai | R. Mehta | assessment_recorded | Assessment:ASM-CRYPTO-KEY-CUSTOPS-2026-Q1-1 |
| 1058 | 2026-04-28 04:00:29 | ai | C. Brennan | assessment_recorded | Assessment:ASM-CRYPTO-KEY-ITSVC-2026-Q1-1 |
| 1059 | 2026-04-28 04:00:30 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CRYPTO-KEY-MKTG-2026-Q1-1 |
| 1060 | 2026-04-28 04:00:31 | ai | L. Okafor | assessment_recorded | Assessment:ASM-CRYPTO-KEY-PAYMENTS-2026-Q1-1 |
| 1061 | 2026-04-28 04:00:32 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-CRYPTO-KEY-PRJ-ATLAS-2026-Q1-1 |
| 1062 | 2026-04-28 04:00:33 | ai | M. Dubois | assessment_recorded | Assessment:ASM-CRYPTO-KEY-PRJ-CORAL-2026-Q1-1 |
| 1063 | 2026-04-28 04:00:34 | ai | R. Mehta | assessment_recorded | Assessment:ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1 |
| 1064 | 2026-04-28 04:00:35 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-DATA-RETENTION-HR-2026-Q1-1 |
| 1065 | 2026-04-28 04:00:36 | ai | C. Brennan | assessment_recorded | Assessment:ASM-DATA-RETENTION-ITSVC-2026-Q1-1 |
| 1066 | 2026-04-28 04:00:37 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-DATA-RETENTION-MKTG-2026-Q1-1 |
| 1067 | 2026-04-28 04:00:38 | ai | L. Okafor | assessment_recorded | Assessment:ASM-DATA-RETENTION-PAYMENTS-2026-Q1-1 |
| 1068 | 2026-04-28 04:00:39 | ai | E. Vasquez | assessment_recorded | Assessment:ASM-DATA-RETENTION-PRJ-ATLAS-2026-Q1-1 |
| 1069 | 2026-04-28 04:00:40 | ai | M. Dubois | assessment_recorded | Assessment:ASM-DATA-RETENTION-PRJ-CORAL-2026-Q1-1 |
| 1070 | 2026-04-28 04:00:41 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-THIRD-PARTY-ACCESS-HR-2026-Q1-1 |
| 1071 | 2026-04-28 04:00:42 | ai | C. Brennan | assessment_recorded | Assessment:ASM-THIRD-PARTY-ACCESS-ITSVC-2026-Q1-1 |
| 1072 | 2026-04-28 04:00:43 | ai | L. Okafor | assessment_recorded | Assessment:ASM-THIRD-PARTY-ACCESS-PAYMENTS-2026-Q1-1 |
| 1073 | 2026-04-28 04:00:44 | ai | N. Iyer | assessment_recorded | Assessment:ASM-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1 |
| 1074 | 2026-04-28 04:00:45 | ai | K. Tanaka | assessment_recorded | Assessment:ASM-THIRD-PARTY-ACCESS-PRJ-BEACON-2026-Q1-1 |
| 1075 | 2026-04-28 04:00:46 | ai | S. Haugen | assessment_recorded | Assessment:ASM-THIRD-PARTY-ACCESS-PROC-2026-Q1-1 |
| 1076 | 2026-04-28 04:00:47 | system | assessor | assessment_completed | Cycle:2026-04-28 |
| 1077 | 2026-04-28 05:00:00 | system | D. Ferreira | flag_raised | Flag:FLG-OVERDUE-ASM-ACCESS-EXPORT-HR-2026-Q1-1 |
| 1078 | 2026-04-28 05:00:01 | ai | D. Ferreira | finding_raised | Finding:FND-ACCESS-EXPORT-HR-2026-Q1 |
| 1079 | 2026-04-28 05:00:02 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-ACCESS-EXPORT-HR-2026-Q1 |
| 1080 | 2026-04-28 05:00:03 | system | L. Okafor | flag_raised | Flag:FLG-OVERDUE-ASM-ACCESS-EXPORT-PAYMENTS-2026-Q1-1 |
| 1081 | 2026-04-28 05:00:04 | ai | L. Okafor | finding_raised | Finding:FND-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 1082 | 2026-04-28 05:00:05 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 1083 | 2026-04-28 05:00:06 | system | R. Mehta | flag_raised | Flag:FLG-GAP-ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 1084 | 2026-04-28 05:00:07 | ai | R. Mehta | finding_raised | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 1085 | 2026-04-28 05:00:08 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 1086 | 2026-04-28 05:00:09 | system | N. Iyer | flag_raised | Flag:FLG-GAP-ASM-BACKUP-VERIFY-PLATFORM-2026-03-1 |
| 1087 | 2026-04-28 05:00:10 | ai | N. Iyer | finding_raised | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-03 |
| 1088 | 2026-04-28 05:00:11 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-03 |
| 1089 | 2026-04-28 05:00:12 | system | D. Ferreira | flag_raised | Flag:FLG-OVERDUE-ASM-CRYPTO-KEY-HR-2026-Q1-1 |
| 1090 | 2026-04-28 05:00:13 | ai | D. Ferreira | finding_raised | Finding:FND-CRYPTO-KEY-HR-2026-Q1 |
| 1091 | 2026-04-28 05:00:14 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-CRYPTO-KEY-HR-2026-Q1 |
| 1092 | 2026-04-28 05:00:15 | system | R. Mehta | flag_raised | Flag:FLG-GAP-ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1 |
| 1093 | 2026-04-28 05:00:16 | ai | R. Mehta | finding_raised | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1094 | 2026-04-28 05:00:17 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1095 | 2026-04-28 05:00:18 | system | C. Brennan | flag_raised | Flag:FLG-GAP-ASM-DATA-RETENTION-ITSVC-2026-Q2-1 |
| 1096 | 2026-04-28 05:00:19 | ai | C. Brennan | finding_raised | Finding:FND-DATA-RETENTION-ITSVC-2026-Q2 |
| 1097 | 2026-04-28 05:00:20 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-DATA-RETENTION-ITSVC-2026-Q2 |
| 1098 | 2026-04-28 05:00:21 | system | E. Vasquez | flag_raised | Flag:FLG-GAP-ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-1 |
| 1099 | 2026-04-28 05:00:22 | ai | E. Vasquez | finding_raised | Finding:FND-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1100 | 2026-04-28 05:00:23 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1101 | 2026-04-28 05:00:24 | system | N. Iyer | flag_raised | Flag:FLG-GAP-ASM-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1-1 |
| 1102 | 2026-04-28 05:00:25 | ai | N. Iyer | finding_raised | Finding:FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 1103 | 2026-04-28 05:00:26 | user | ID-PA-KAUR | finding_severity_assigned | Finding:FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 1104 | 2026-04-28 05:00:27 | system | flagging | flagging_completed | Cycle:2026-04-28 |
| 1105 | 2026-04-28 05:30:00 | system | J. Alvarez | finding_reminder_sent | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 1106 | 2026-04-28 05:30:01 | system | ID-ALVAREZ | notification_logged | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 1107 | 2026-04-28 05:30:02 | system | K. Tanaka | finding_reminder_sent | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1108 | 2026-04-28 05:30:03 | system | ID-TANAKA | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1109 | 2026-04-28 05:30:04 | system | N. Iyer | finding_escalated | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1110 | 2026-04-28 05:30:05 | system | ID-IYER | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1111 | 2026-04-28 05:30:06 | system | ID-PA-KAUR | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1112 | 2026-04-28 05:30:07 | system | ID-PA-OSEI | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1113 | 2026-04-28 05:30:08 | system | H. Lindqvist | finding_escalated | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1114 | 2026-04-28 05:30:09 | system | ID-DIRECTOR | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1115 | 2026-04-28 05:30:10 | system | ID-PA-KAUR | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1116 | 2026-04-28 05:30:11 | system | ID-PA-OSEI | notification_logged | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1117 | 2026-04-28 05:30:12 | system | E. Vasquez | finding_reminder_sent | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 1118 | 2026-04-28 05:30:13 | system | ID-VASQUEZ | notification_logged | Finding:FND-CUST-COMPLAINTS-PRJ-ATLAS-2026-02 |
| 1119 | 2026-04-28 05:30:14 | system | J. Alvarez | finding_reminder_sent | Finding:FND-DPIA-MKTG-2026 |
| 1120 | 2026-04-28 05:30:15 | system | ID-ALVAREZ | notification_logged | Finding:FND-DPIA-MKTG-2026 |
| 1121 | 2026-04-28 05:30:16 | system | R. Mehta | finding_reminder_sent | Finding:FND-IA-2026-H1-02 |
| 1122 | 2026-04-28 05:30:17 | system | ID-MEHTA | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1123 | 2026-04-28 05:30:18 | system | M. Castellanos | finding_escalated | Finding:FND-IA-2026-H1-02 |
| 1124 | 2026-04-28 05:30:19 | system | ID-OPSDIR | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1125 | 2026-04-28 05:30:20 | system | ID-PA-KAUR | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1126 | 2026-04-28 05:30:21 | system | ID-PA-OSEI | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1127 | 2026-04-28 05:30:22 | system | H. Lindqvist | finding_escalated | Finding:FND-IA-2026-H1-02 |
| 1128 | 2026-04-28 05:30:23 | system | ID-DIRECTOR | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1129 | 2026-04-28 05:30:24 | system | ID-PA-KAUR | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1130 | 2026-04-28 05:30:25 | system | ID-PA-OSEI | notification_logged | Finding:FND-IA-2026-H1-02 |
| 1131 | 2026-04-28 05:30:26 | system | A. Novak | finding_reminder_sent | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1132 | 2026-04-28 05:30:27 | system | ID-NOVAK | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1133 | 2026-04-28 05:30:28 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1134 | 2026-04-28 05:30:29 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1135 | 2026-04-28 05:30:30 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1136 | 2026-04-28 05:30:31 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1137 | 2026-04-28 05:30:32 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1138 | 2026-04-28 05:30:33 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1139 | 2026-04-28 05:30:34 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1140 | 2026-04-28 05:30:35 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1141 | 2026-04-28 05:30:36 | system | C. Brennan | finding_reminder_sent | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 1142 | 2026-04-28 05:30:37 | system | ID-BRENNAN | notification_logged | Finding:FND-INCIDENT-PM-ITSVC-2026-01 |
| 1143 | 2026-04-28 05:30:38 | system | N. Iyer | finding_reminder_sent | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1144 | 2026-04-28 05:30:39 | system | ID-IYER | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1145 | 2026-04-28 05:30:40 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1146 | 2026-04-28 05:30:41 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1147 | 2026-04-28 05:30:42 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1148 | 2026-04-28 05:30:43 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1149 | 2026-04-28 05:30:44 | system | H. Lindqvist | finding_escalated | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1150 | 2026-04-28 05:30:45 | system | ID-DIRECTOR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1151 | 2026-04-28 05:30:46 | system | ID-PA-KAUR | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1152 | 2026-04-28 05:30:47 | system | ID-PA-OSEI | notification_logged | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1153 | 2026-04-28 05:30:48 | system | follow-up | followup_completed | Cycle:2026-04-28 |
| 1154 | 2026-04-28 06:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0808 |
| 1155 | 2026-04-28 06:00:01 | user | R. Mehta | remediation_submitted | CheckInstance:CHK-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 1156 | 2026-04-28 06:00:02 | user | ID-MEHTA | finding_progress_recorded | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 1157 | 2026-04-28 06:00:03 | user | R. Mehta | evidence_round_opened | EvidenceSubmission:SUB-ACCESS-REVIEW-CUSTOPS-2026-Q1-R1 |
| 1158 | 2026-04-28 06:00:04 | ai | R. Mehta | assessment_recorded | Assessment:ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-2 |
| 1159 | 2026-04-28 06:00:05 | system | R. Mehta | assessment_superseded | Assessment:ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 1160 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-ACCESS-REVIEW-CUSTOPS-2026-Q1-R1 |
| 1161 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 1162 | 2026-04-28 06:00:08 | system | R. Mehta | flag_closed | Flag:FLG-GAP-ASM-ACCESS-REVIEW-CUSTOPS-2026-Q1-1 |
| 1163 | 2026-04-28 06:00:00 | user | J. Alvarez | evidence_bound | Evidence:EV-SUB-0848 |
| 1164 | 2026-04-28 06:00:01 | user | J. Alvarez | remediation_submitted | CheckInstance:CHK-CHANGE-MGMT-MKTG-2026-02 |
| 1165 | 2026-04-28 06:00:02 | user | ID-ALVAREZ | finding_progress_recorded | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 1166 | 2026-04-28 06:00:03 | user | J. Alvarez | evidence_round_opened | EvidenceSubmission:SUB-CHANGE-MGMT-MKTG-2026-02-R1 |
| 1167 | 2026-04-28 06:00:04 | ai | J. Alvarez | assessment_recorded | Assessment:ASM-CHANGE-MGMT-MKTG-2026-02-2 |
| 1168 | 2026-04-28 06:00:05 | system | J. Alvarez | assessment_superseded | Assessment:ASM-CHANGE-MGMT-MKTG-2026-02-1 |
| 1169 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-CHANGE-MGMT-MKTG-2026-02-R1 |
| 1170 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 1171 | 2026-04-28 06:00:08 | system | J. Alvarez | flag_closed | Flag:FLG-GAP-ASM-CHANGE-MGMT-MKTG-2026-02-1 |
| 1172 | 2026-04-28 06:00:00 | user | K. Tanaka | evidence_bound | Evidence:EV-SUB-0866 |
| 1173 | 2026-04-28 06:00:01 | user | K. Tanaka | remediation_submitted | CheckInstance:CHK-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1174 | 2026-04-28 06:00:02 | user | ID-TANAKA | finding_progress_recorded | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1175 | 2026-04-28 06:00:03 | user | K. Tanaka | evidence_round_opened | EvidenceSubmission:SUB-CHANGE-MGMT-PRJ-BEACON-2026-02-R1 |
| 1176 | 2026-04-28 06:00:04 | ai | K. Tanaka | assessment_recorded | Assessment:ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-2 |
| 1177 | 2026-04-28 06:00:05 | system | K. Tanaka | assessment_superseded | Assessment:ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1 |
| 1178 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-CHANGE-MGMT-PRJ-BEACON-2026-02-R1 |
| 1179 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1180 | 2026-04-28 06:00:08 | system | K. Tanaka | flag_closed | Flag:FLG-GAP-ASM-CHANGE-MGMT-PRJ-BEACON-2026-02-1 |
| 1181 | 2026-04-28 06:00:00 | user | R. Mehta | evidence_bound | Evidence:EV-SUB-0894 |
| 1182 | 2026-04-28 06:00:01 | user | R. Mehta | remediation_submitted | CheckInstance:CHK-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1183 | 2026-04-28 06:00:02 | user | ID-MEHTA | finding_progress_recorded | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1184 | 2026-04-28 06:00:03 | user | R. Mehta | evidence_round_opened | EvidenceSubmission:SUB-DATA-RETENTION-CUSTOPS-2026-Q1-R1 |
| 1185 | 2026-04-28 06:00:04 | ai | R. Mehta | assessment_recorded | Assessment:ASM-DATA-RETENTION-CUSTOPS-2026-Q1-2 |
| 1186 | 2026-04-28 06:00:05 | system | R. Mehta | assessment_superseded | Assessment:ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1 |
| 1187 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-DATA-RETENTION-CUSTOPS-2026-Q1-R1 |
| 1188 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1189 | 2026-04-28 06:00:08 | system | R. Mehta | flag_closed | Flag:FLG-GAP-ASM-DATA-RETENTION-CUSTOPS-2026-Q1-1 |
| 1190 | 2026-04-28 06:00:00 | user | C. Brennan | evidence_bound | Evidence:EV-SUB-0898 |
| 1191 | 2026-04-28 06:00:01 | user | C. Brennan | remediation_submitted | CheckInstance:CHK-DATA-RETENTION-ITSVC-2026-Q2 |
| 1192 | 2026-04-28 06:00:02 | user | ID-BRENNAN | finding_progress_recorded | Finding:FND-DATA-RETENTION-ITSVC-2026-Q2 |
| 1193 | 2026-04-28 06:00:03 | user | C. Brennan | evidence_round_opened | EvidenceSubmission:SUB-DATA-RETENTION-ITSVC-2026-Q2-R1 |
| 1194 | 2026-04-28 06:00:04 | system | C. Brennan | assessment_recorded | Assessment:ASM-DATA-RETENTION-ITSVC-2026-Q2-2 |
| 1195 | 2026-04-28 06:00:05 | system | C. Brennan | assessment_superseded | Assessment:ASM-DATA-RETENTION-ITSVC-2026-Q2-1 |
| 1196 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_insufficient | EvidenceSubmission:SUB-DATA-RETENTION-ITSVC-2026-Q2-R1 |
| 1197 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | evidence_found_insufficient | Finding:FND-DATA-RETENTION-ITSVC-2026-Q2 |
| 1198 | 2026-04-28 06:00:00 | user | A. Novak | evidence_bound | Evidence:EV-SUB-0911 |
| 1199 | 2026-04-28 06:00:01 | user | A. Novak | remediation_submitted | CheckInstance:CHK-INCIDENT-PM-FINREP-2026-02 |
| 1200 | 2026-04-28 06:00:02 | user | ID-NOVAK | finding_progress_recorded | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1201 | 2026-04-28 06:00:03 | user | A. Novak | evidence_round_opened | EvidenceSubmission:SUB-INCIDENT-PM-FINREP-2026-02-R1 |
| 1202 | 2026-04-28 06:00:04 | ai | A. Novak | assessment_recorded | Assessment:ASM-INCIDENT-PM-FINREP-2026-02-2 |
| 1203 | 2026-04-28 06:00:05 | system | A. Novak | assessment_superseded | Assessment:ASM-INCIDENT-PM-FINREP-2026-02-1 |
| 1204 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-INCIDENT-PM-FINREP-2026-02-R1 |
| 1205 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-INCIDENT-PM-FINREP-2026-02 |
| 1206 | 2026-04-28 06:00:08 | system | A. Novak | flag_closed | Flag:FLG-GAP-ASM-INCIDENT-PM-FINREP-2026-02-1 |
| 1207 | 2026-04-28 06:00:00 | user | N. Iyer | evidence_bound | Evidence:EV-SUB-0920 |
| 1208 | 2026-04-28 06:00:01 | user | N. Iyer | remediation_submitted | CheckInstance:CHK-INCIDENT-PM-PLATFORM-2026-02 |
| 1209 | 2026-04-28 06:00:02 | user | ID-IYER | finding_progress_recorded | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1210 | 2026-04-28 06:00:03 | user | N. Iyer | evidence_round_opened | EvidenceSubmission:SUB-INCIDENT-PM-PLATFORM-2026-02-R1 |
| 1211 | 2026-04-28 06:00:04 | ai | N. Iyer | assessment_recorded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-02-2 |
| 1212 | 2026-04-28 06:00:05 | system | N. Iyer | assessment_superseded | Assessment:ASM-INCIDENT-PM-PLATFORM-2026-02-1 |
| 1213 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-INCIDENT-PM-PLATFORM-2026-02-R1 |
| 1214 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-INCIDENT-PM-PLATFORM-2026-02 |
| 1215 | 2026-04-28 06:00:08 | system | N. Iyer | flag_closed | Flag:FLG-GAP-ASM-INCIDENT-PM-PLATFORM-2026-02-1 |
| 1216 | 2026-04-28 06:00:00 | user | E. Vasquez | evidence_bound | Evidence:EV-SUB-0926 |
| 1217 | 2026-04-28 06:00:01 | user | E. Vasquez | remediation_submitted | CheckInstance:CHK-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1218 | 2026-04-28 06:00:02 | user | ID-VASQUEZ | finding_progress_recorded | Finding:FND-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1219 | 2026-04-28 06:00:03 | user | E. Vasquez | evidence_round_opened | EvidenceSubmission:SUB-INCIDENT-PM-PRJ-ATLAS-2026-04-R1 |
| 1220 | 2026-04-28 06:00:04 | system | E. Vasquez | assessment_recorded | Assessment:ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-2 |
| 1221 | 2026-04-28 06:00:05 | system | E. Vasquez | assessment_superseded | Assessment:ASM-INCIDENT-PM-PRJ-ATLAS-2026-04-1 |
| 1222 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_insufficient | EvidenceSubmission:SUB-INCIDENT-PM-PRJ-ATLAS-2026-04-R1 |
| 1223 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | evidence_found_insufficient | Finding:FND-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1224 | 2026-04-28 07:00:00 | ai | D. Ferreira | finding_classified | Finding:FND-ACCESS-EXPORT-HR-2026-Q1 |
| 1225 | 2026-04-28 07:00:01 | ai | L. Okafor | finding_classified | Finding:FND-ACCESS-EXPORT-PAYMENTS-2026-Q1 |
| 1226 | 2026-04-28 07:00:02 | ai | R. Mehta | finding_classified | Finding:FND-ACCESS-REVIEW-CUSTOPS-2026-Q1 |
| 1227 | 2026-04-28 07:00:03 | ai | N. Iyer | finding_classified | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-03 |
| 1228 | 2026-04-28 07:00:04 | ai | D. Ferreira | finding_classified | Finding:FND-CRYPTO-KEY-HR-2026-Q1 |
| 1229 | 2026-04-28 07:00:05 | ai | R. Mehta | finding_classified | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1230 | 2026-04-28 07:00:06 | ai | C. Brennan | finding_classified | Finding:FND-DATA-RETENTION-ITSVC-2026-Q2 |
| 1231 | 2026-04-28 07:00:07 | ai | E. Vasquez | finding_classified | Finding:FND-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1232 | 2026-04-28 07:00:08 | ai | N. Iyer | finding_classified | Finding:FND-THIRD-PARTY-ACCESS-PLATFORM-2026-Q1 |
| 1233 | 2026-04-28 07:30:00 | ai | A. Novak | recurrence_examined | Finding:FND-CHANGE-MGMT-FINREP-2026-02 |
| 1234 | 2026-04-28 07:30:01 | ai | J. Alvarez | recurrence_examined | Finding:FND-CHANGE-MGMT-MKTG-2026-02 |
| 1235 | 2026-04-28 07:30:02 | ai | K. Tanaka | recurrence_examined | Finding:FND-CHANGE-MGMT-PRJ-BEACON-2026-02 |
| 1236 | 2026-04-28 07:30:03 | ai | N. Iyer | recurrence_examined | Finding:FND-BACKUP-VERIFY-PLATFORM-2026-03 |
| 1237 | 2026-04-28 07:30:04 | ai | D. Ferreira | recurrence_examined | Finding:FND-CRYPTO-KEY-HR-2026-Q1 |
| 1238 | 2026-04-28 07:30:05 | ai | R. Mehta | recurrence_examined | Finding:FND-DATA-RETENTION-CUSTOPS-2026-Q1 |
| 1239 | 2026-04-28 07:30:06 | ai | C. Brennan | recurrence_examined | Finding:FND-DATA-RETENTION-ITSVC-2026-Q2 |
| 1240 | 2026-04-28 07:30:07 | ai | E. Vasquez | recurrence_examined | Finding:FND-INCIDENT-PM-PRJ-ATLAS-2026-04 |
| 1241 | 2026-04-28 07:30:08 | ai | E. Vasquez | recurrence_examined | Finding:FND-QA-2026-Q2-02 |
| 1242 | 2026-04-28 07:30:09 | ai | S. Haugen | recurrence_examined | Finding:FND-DOC-2026-09-01 |
| 1243 | 2026-04-28 07:30:10 | ai | J. Alvarez | recurrence_examined | Finding:FND-IA-2026-H2-02 |
| 1244 | 2026-04-28 07:30:11 | ai | K. Tanaka | recurrence_examined | Finding:FND-QA-2027-Q1-02 |
| 1245 | 2026-04-28 07:30:12 | ai | M. Dubois | recurrence_examined | Finding:FND-REL-2027-04-01 |
| 1246 | 2026-04-28 09:30:00 | user | D. Ferreira | evidence_uploaded | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 1247 | 2026-04-28 06:00:00 | user | D. Ferreira | evidence_bound | Evidence:EV-SUB-UI-0960 |
| 1248 | 2026-04-28 06:00:01 | user | D. Ferreira | remediation_submitted | CheckInstance:CHK-CRYPTO-KEY-HR-2026-Q1 |
| 1249 | 2026-04-28 06:00:02 | user | ID-FERREIRA | finding_progress_recorded | Finding:FND-CRYPTO-KEY-HR-2026-Q1 |
| 1250 | 2026-04-28 06:00:03 | user | D. Ferreira | evidence_round_opened | EvidenceSubmission:SUB-CRYPTO-KEY-HR-2026-Q1-R1 |
| 1251 | 2026-04-28 06:00:04 | ai | D. Ferreira | assessment_recorded | Assessment:ASM-CRYPTO-KEY-HR-2026-Q1-2 |
| 1252 | 2026-04-28 06:00:05 | system | D. Ferreira | assessment_superseded | Assessment:ASM-CRYPTO-KEY-HR-2026-Q1-1 |
| 1253 | 2026-04-28 06:00:06 | user | P. Kaur | evidence_round_accepted | EvidenceSubmission:SUB-CRYPTO-KEY-HR-2026-Q1-R1 |
| 1254 | 2026-04-28 06:00:07 | user | ID-PA-KAUR | finding_closed | Finding:FND-CRYPTO-KEY-HR-2026-Q1 |
| 1255 | 2026-04-28 06:00:08 | system | D. Ferreira | flag_closed | Flag:FLG-OVERDUE-ASM-CRYPTO-KEY-HR-2026-Q1-1 |
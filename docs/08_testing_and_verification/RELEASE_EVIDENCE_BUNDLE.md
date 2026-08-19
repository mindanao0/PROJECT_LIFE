# Signed Release Evidence Bundling Protocol

> **Subsystem:** Release Evidence & Verification Manifests  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.    
> **Chain formula:** [`spec/ACTIVE_CONTRACT.md`](../../spec/ACTIVE_CONTRACT.md) section 18.1  
> ไฟล์นี้เคยเขียน `genesis_hash` เป็น 64 zeros พร้อม prefix `sha256:` ขณะที่ §18.1 เขียนว่า `null` — ตอนนี้ตรงกันแล้วคือคอลัมน์เก็บ NULL ส่วนค่าที่เข้าสูตรคือ 32 zero **bytes** แก้ที่ CR-0006
> **Scope:** `REQ-S18-001` .. `REQ-S18-003`

---

## 1. Evidence Bundle JSON Manifest Structure

```json
{
  "evidence_bundle_version": "1.0.0",
  "bundle_id": "evid-release-10.2.2-001",
  "engine_version": "10.2.2",
  "maturity_level_verified": "M11",
  "created_at_utc": "2026-08-18T14:40:00Z",
  "environment_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "golden_corpus_results": {
    "total_projects": 14,
    "passed_projects": 14,
    "failed_projects": 0
  },
  "audit_hash_chain": {
    "chain_length": 1420,
    "genesis_previous_digest": "0000000000000000000000000000000000000000000000000000000000000000",
    "head_hash": "sha256:8f4c2e3a1b5d6c7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e"
  },
  "multisig_signatures": [
    {
      "key_id": "sha256:pubkey_lead_engineer_01",
      "algorithm": "Ed25519",
      "signature": "64_bytes_ed25519_signature_base64url..."
    },
    {
      "key_id": "sha256:pubkey_security_auditor_02",
      "algorithm": "Ed25519",
      "signature": "64_bytes_ed25519_signature_base64url..."
    }
  ]
}
```

- **[REQ-S18-001]** หลักฐาน Evidence ทั้งหมดต้องเป็น Immutable และลงนามด้วย EE-CRYPTO-1 Profile

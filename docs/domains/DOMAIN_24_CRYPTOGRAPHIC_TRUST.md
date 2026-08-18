# Domain 24: Cryptographic Trust (EE-CRYPTO-1, Ed25519)

> **Domain Index:** `DOMAIN-24`  
> **Engineering Scope:** `DIM-231` .. `DIM-240`  
> **Mathematical Equations:** `EQ-231` .. `EQ-240`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 24 กำหนดความน่าเชื่อถือทางวิทยาการรหัสลับ (Cryptographic Trust Profile **EE-CRYPTO-1**) ผ่าน **Ed25519 Digital Signatures**, **Twisted Edwards Curve Math**, **2-of-3 Multisig Quorum Enforcement**, **Merkle Hash Chain Inductive Recurrence**, และการขจัดช่องโหว่ Downgrade Attacks.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-231  │ EQ-231   │ EE-CRYPTO-1 Standard Profile Tuple        │ <Ed25519, SHA-256, Raw32, Raw64>                            │
│ DIM-232  │ EQ-232   │ Ed25519 Twisted Edwards Curve Equation    │ -x^2 + y^2 = 1 + d*x^2*y^2 (mod 2^{255}-19), d = -121665/121666│
│ DIM-233  │ EQ-233   │ Zero Algorithm Negotiation Downgrade Guard│ |AllowedAlgos| === 1                                        │
│ DIM-234  │ EQ-234   │ 2-of-3 Multisig Quorum Verification       │ sum_{i=1}^3 VerifySig(K_i, M, S_i) >= 2                     │
│ DIM-235  │ EQ-235   │ Cryptographic Nonce Entropy Lower Bound   │ H(Nonce) >= 128 bits                                        │
│ DIM-236  │ EQ-236   │ RFC 8032 Schnorr Signature Verification   │ S * B = R + k * A (mod l), k = SHA-512(R || A || M)         │
│ DIM-237  │ EQ-237   │ Key Identifier SHA-256 Hash Derivation    │ KeyID = SHA-256(PublicKeyBytes)                             │
│ DIM-238  │ EQ-238   │ Ephemeral Key Ceremony Verification Hash  │ H_ceremony = SHA-256(product K_witness)                     │
│ DIM-239  │ EQ-239   │ Key Compromise Revocation List Invariant  │ KeyID not in RevocationList                                 │
│ DIM-240  │ EQ-240   │ Merkle Hash Chain Inductive Recurrence    │ H_i = SHA-256(H_{i-1} || EventBytes_i || Seq_i)             │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-231` / `EQ-231`: EE-CRYPTO-1 Standard Profile Tuple
- โปรไฟล์การเข้ารหัสมาตรฐานแบบตรึงรูป (Pinned Cryptographic Profile):
  $$\langle \text{Ed25519}, \text{SHA-256}, \text{Raw32}, \text{Raw64} \rangle$$

### `DIM-232` / `EQ-232`: Ed25519 Twisted Edwards Curve
- เส้นโค้งเอลลิปติกบน Finite Field $\mathbb{F}_{2^{255}-19}$ สำหรับเซ็นและตรวจสอบลายเซ็นดิจิทัล:
  $$-x^2 + y^2 = 1 + d x^2 y^2 \pmod{2^{255} - 19}, \qquad d = -\frac{121665}{121666}$$

### `DIM-233` / `EQ-233`: Zero Algorithm Negotiation Downgrade Guard
- ห้ามเจรจาเปลี่ยนอัลกอริทึมเข้ารหัสเพื่อป้องกัน Downgrade Attack:
  $$|\text{AllowedAlgos}| \equiv 1$$

### `DIM-234` / `EQ-234`: 2-of-3 Multisig Quorum Verification
- การอนุมัติ Release สู่ Production ในระดับ M12 ต้องมีลายเซ็นที่ถูกต้องอย่างน้อย 2 ใน 3 กุญแจ:
  $$\sum_{i=1}^3 \text{VerifySig}(K_i, M, S_i) \ge 2$$

### `DIM-235` / `EQ-235`: Cryptographic Nonce Entropy Lower Bound
- Nonce ต้องมีความแปรปรวนเชิงเอนโทรปีอย่างน้อย 128 บิต:
  $$H(\text{Nonce}) \ge 128 \quad \text{bits}$$

### `DIM-236` / `EQ-236`: RFC 8032 Schnorr Signature Verification
- การตรวจสอบลายเซ็นดิจิทัล:
  $$S \cdot B = R + k \cdot A \pmod \ell, \qquad k = \text{SHA-512}(R \parallel A \parallel M)$$

### `DIM-237` / `EQ-237`: Key Identifier SHA-256 Hash Derivation
- การระบุตัวตนของ Public Key ด้วย KeyID:
  $$\text{KeyID} = \text{SHA-256}(\text{PublicKeyBytes})$$

### `DIM-238` / `EQ-238`: Ephemeral Key Ceremony Verification Hash
- การบันทึกและตรวจสอบพิธีสร้างกุญแจชั่วคราว:
  $$H_{\text{ceremony}} = \text{SHA-256}\left(\prod K_{\text{witness}}\right)$$

### `DIM-239` / `EQ-239`: Key Compromise Revocation List Invariant
- ปฏิเสธกุญแจที่ถูกระบุในรายการเพิกถอน (Revocation List):
  $$\text{KeyID} \notin \text{RevocationList}$$

### `DIM-240` / `EQ-240`: Merkle Hash Chain Inductive Recurrence
- การรักษาสายโซ่ความสมบูรณ์ของ Audit Trail:
  $$H_i = \text{SHA-256}(H_{i-1} \parallel \text{EventBytes}_i \parallel \text{Seq}_i)$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D24-01` [Ed25519 Test Vectors]:** ตรวจสอบลายเซ็นกับ RFC 8032 Official Test Vectors ต้องถูกต้อง 100%
2. **Test `TC-D24-02` [Multisig Threshold]:** ทดสอบส่ง Evidence Bundle ที่มี 1 Signature (ไม่ครบ 2) ระบบต้องปฏิเสธ
3. **Test `TC-D24-03` [Revoked Key Denial]:** ยื่นลายเซ็นที่สร้างจาก Revoked Key ตรวจสอบว่าระบบบล็อกการโหลด
4. **Test `TC-D24-04` [Merkle Chain Integrity]:** แก้ไขข้อมูล Event ย้อนหลัง 1 ไบต์ ตรวจสอบว่าระบบตรวจพบ Hash Mismatch ทันที

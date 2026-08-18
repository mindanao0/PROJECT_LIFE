# Cryptographic Trust Profile Specification (EE-CRYPTO-1)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** SECURITY SPECIFICATION (L0 Authority)
> **Target Subsystem:** Cryptographic Key Management & Verification  
> **Governing Equations:** `EQ-231` .. `EQ-240` (Ed25519, Twisted Edwards Curve, Multisig 2-of-3)

---

## 1. The EE-CRYPTO-1 Standard Specification

โปรไฟล์การเข้ารหัส **`EE-CRYPTO-1`** กำหนดสถาปัตยกรรมความปลอดภัยแบบไม่มีการต่อรอง (Zero Negotiation):
$$\text{EE-CRYPTO-1} = \langle \text{Algorithm: Ed25519}, \text{Hash: SHA-256}, \text{KeyFormat: Raw32}, \text{SigFormat: Raw64} \rangle$$

---

## 2. Twisted Edwards Curve Mathematics & RFC 8032 Verification

1. **Curve Equation:**
   $$-x^2 + y^2 = 1 + d x^2 y^2 \pmod{2^{255} - 19}, \qquad d = -\frac{121665}{121666}$$
2. **Signature Verification (RFC 8032):**
   $$S \cdot B = R + k \cdot A \pmod \ell, \qquad k = \text{SHA-512}(R \parallel A \parallel M)$$

---

## 3. Multi-Party Quorum Threshold (2-of-3 Multisig)

การรับรอง Release Package สู่ Production (Maturity M12) ต้องผ่านลายเซ็นดิจิทัลที่ถูกต้องอย่างน้อย 2 ใน 3 กุญแจ:
$$\sum_{i=1}^3 \text{VerifySig}(K_i, M, S_i) \ge 2$$
และบันทึก Key Identifiers (`KeyID = SHA-256(PublicKey)`) ลงใน Signed Manifest

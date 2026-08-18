# Deployment & Canary Rollout FSM Specification (8 States)

> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** FSM SPECIFICATION (L2 Authority)
> **Target Subsystem:** Safe Export & Production Canary Rollout  
> **Governing Equations:** `EQ-026` (Canary Traffic Split), `EQ-027` (Hazard Function Rollback), `EQ-289` (Self-Containment)

---

## 1. Complete 8-State Topology

วงจรสถานะการส่งออกโค้ดที่ผ่านการวิวัฒนาการและการนำขึ้นระบบจริง (8 Deployment States):

```text
       [EXPORT_PREPARED] (Safe Default Mode)
              │
              ▼
       [SIGNATURE_VERIFIED]
              │
              ▼
       [PACKAGE_BUNDLED]
              │
              ▼
       [CANARY_PROVISIONED] ────────┐ (Hazard Rate > 0.01)
              │                     │
              ▼                     ▼
       [CANARY_EVALUATING] ────► [ROLLED_BACK]
              │
              ▼
       [PROMOTED_FULL_TRAFFIC]
              │
              ▼
       [ARCHIVED_PRODUCTION]
```

### 1.1 Formal State Definitions
1. `EXPORT_PREPARED`: โหมดเริ่มต้น `SAFE_EXPORT_ONLY` สร้าง Export Directory ที่แยกขาดจากระบบ
2. `SIGNATURE_VERIFIED`: ตรวจสอบลายเซ็น Ed25519 ของ Release Evidence Bundle
3. `PACKAGE_BUNDLED`: รวมไฟล์โค้ด, dependencies และ Wheel/Tarball แบบ Standalone
4. `CANARY_PROVISIONED`: เตรียมสภาพแวดล้อม Canary Rollout (แยก Namespace)
5. `CANARY_EVALUATING`: ทยอยส่ง Traffic สดตามสัดส่วน $\alpha \cdot t$ พร้อมมอนิเตอร์ Latency & Error Rate
6. `PROMOTED_FULL_TRAFFIC`: ผ่านการประเมิน Canary 100% เลื่อนระดับเป็น Main Production
7. `ROLLED_BACK`: ตรวจพบ Regression หรือ Error Rate $> 1\%$ สั่งสลับ Traffic กลับระบบเดิมภายใน 1s
8. `ARCHIVED_PRODUCTION`: บันทึกประวัติและ Digest ของ Deployment เข้าสู่ระบบคลังข้อมูลถาวร

---

## 2. Automated Rollback Hazard Equation

ระบบมอนิเตอร์ Hazard Function ตลอดเวลาในช่วง Canary:
$$\lambda_{\text{rollback}}(t) = \mathbb{I}(\text{ErrorRate}(t) > 0.01 \lor \text{P99\_Latency}(t) > 1.15 \times \text{Baseline})$$
หาก $\lambda_{\text{rollback}}(t) = 1$ ระบบจะตัด Traffic และเปลี่ยนสถานะสู่ `ROLLED_BACK` ภายในเวลา $\le 1.0\text{ วินาที}$

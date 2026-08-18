# 02 — Finite State Machines (FSM) Specification

> **Active Requirements Covered:** `REQ-S08-001` .. `REQ-S08-012`, `REQ-S14-001` .. `REQ-S14-002`, `REQ-S19-001` .. `REQ-S19-003`  
> **Authority Level:** NORMATIVE

Evolution Engine ควบคุมวงจรชีวิตของ Entity สำคัญทุกตัวด้วย Finite State Machine ที่มีนิยามชัดเจน (Formal, Deterministic, Reachable และปราศจาก Deadlock) จำนวน 5 ชุดหลัก:

---

## 1. Candidate Lifecycle State Machine (17 States)

ควบคุมวงจรชีวิตตั้งแต่สร้าง Candidate Code จนถึงการประเมินและคัดเลือก

```text
       ┌───────────┐
       │  CREATED  │
       └─────┬─────┘
             │
             ▼
       ┌──────────────┐
       │ MATERIALIZED │
       └─────┬────────┘
             │
             ▼
     ┌──────────────────┐
     │ STATIC_VALIDATED │
     └───────┬──────────┘
             │
             ▼
     ┌──────────────────┐
     │ POLICY_VALIDATED │
     └───────┬──────────┘
             │
             ▼
    ┌────────────────────┐
    │ SECURITY_VALIDATED ├────────────────┐
    └────────┬───────────┘                │
             │                            │
             ▼                            ▼
      ┌───────────────┐            ┌─────────────┐
      │ SANDBOX_READY │            │ QUARANTINED │ (Terminal for security breach)
      └──────┬────────┘            └─────────────┘
             │                            ▲
             ▼                            │
        ┌───────────┐                     │
        │ EXECUTING ├─────────────────────┘
        └────┬──────┘
             │
             ▼
        ┌───────────┐
        │  EXECUTED │
        └────┬──────┘
             │
             ▼
        ┌───────────┐
        │  TESTING  │
        └────┬──────┘
             │
             ▼
     ┌─────────────────┐
     │ ORACLE_VERIFIED │
     └───────┬─────────┘
             │
             ▼
   ┌─────────────────────┐
   │ CAPABILITY_VERIFIED │
   └─────────┬───────────┘
             │
             ▼
    ┌──────────────────┐
    │ METRIC_EVALUATED │
    └────────┬─────────┘
             │
             ▼
    ┌───────────────────┐
    │ EVIDENCE_VERIFIED │
    └────────┬──────────┘
             │
             ▼
        ┌──────────┐
        │ ELIGIBLE │
        └────┬─────┘
             │
   ┌─────────┴─────────┐
   ▼                   ▼
┌──────────┐     ┌──────────┐
│ SELECTED │     │ REJECTED │
└──────────┘     └──────────┘
(Terminal Elite) (Terminal Invalid/Failed)
```

- **All States:** `CREATED`, `MATERIALIZED`, `STATIC_VALIDATED`, `POLICY_VALIDATED`, `SECURITY_VALIDATED`, `SANDBOX_READY`, `EXECUTING`, `EXECUTED`, `TESTING`, `ORACLE_VERIFIED`, `CAPABILITY_VERIFIED`, `METRIC_EVALUATED`, `EVIDENCE_VERIFIED`, `ELIGIBLE`, `SELECTED`, `REJECTED`, `QUARANTINED`
- **Terminal States:** `SELECTED`, `REJECTED`, `QUARANTINED`
- **Execution Outcomes (ไม่ใช่ lifecycle state):** `SUCCESS`, `TIMEOUT`, `CRASHED`, `OOM`, `RESOURCE_EXCEEDED`, `SECURITY_VIOLATION`
  - `TIMEOUT / CRASHED / OOM / RESOURCE_EXCEEDED` $\rightarrow$ Map to `REJECTED`
  - `SECURITY_VIOLATION` $\rightarrow$ Map to `QUARANTINED`

---

## 2. Run State Machine (11 States)

ควบคุมวงจรชีวิตของการรัน Evolution Engine 1 รอบการประมวลผล

```text
         ┌─────────┐
         │ CREATED │
         └────┬────┘
              │
              ▼
        ┌────────────┐
        │ VALIDATING ├───────────────┐
        └─────┬──────┘               │
              │                      │
              ▼                      ▼
           ┌───────┐             ┌────────┐
           │ READY │             │ FAILED │ (Terminal)
           └───┬───┘             └────────┘
               │                      ▲
               ▼                      │
     ┌───────────────────┐            │
     │      RUNNING      ├────────────┤
     └──┬───┬────────┬───┘            │
        │   │        │                │
┌───────┘   │        └────────────┐   │
│           ▼                     │   │
│      ┌─────────┐           ┌────┴───┴───┐
│      │ PAUSING │           │ RECOVERING │
│      └────┬────┘           └────┬───┬───┘
│           │                     │   │
│           ▼                     │   │
│       ┌────────┐                │   │
│       │ PAUSED ├────────────────┘   │
│       └───┬────┘                    │
│           │                         │
│           ▼                         │
│      ┌──────────┐                   │
│      │ STOPPING ├───────────────────┘
│      └────┬─────┘
│           │
▼           ▼
┌──────────────────┐       ┌───────────┐
│     STOPPED      │       │ COMPLETED │
└──────────────────┘       └───────────┘
(Terminal User Stop)       (Terminal Success)
```

- **Transitions:**
  - `CREATED` $\rightarrow$ `VALIDATING` | `STOPPED`
  - `VALIDATING` $\rightarrow$ `READY` | `FAILED`
  - `READY` $\rightarrow$ `RUNNING` | `STOPPED`
  - `RUNNING` $\rightarrow$ `PAUSING` | `STOPPING` | `COMPLETED` | `FAILED` | `RECOVERING`
  - `PAUSING` $\rightarrow$ `PAUSED` | `FAILED` | `RECOVERING`
  - `PAUSED` $\rightarrow$ `RUNNING` | `STOPPING` | `RECOVERING`
  - `STOPPING` $\rightarrow$ `STOPPED` | `FAILED` | `RECOVERING`
  - `RECOVERING` $\rightarrow$ `RUNNING` | `PAUSED` | `STOPPED` | `FAILED`
- **Terminal States:** `STOPPED`, `COMPLETED`, `FAILED`

---

## 3. Recovery State Machine (9 States)

ควบคุมขั้นตอนการกู้คืนสถานะหลังระบบขัดข้องหรือเกิด Crash

```text
  ┌───────────┐
  │ REQUESTED │
  └─────┬─────┘
        │
        ▼
┌───────────────────┐
│ VALIDATING_INPUTS │
└───────┬───────────┘
        │
        ▼
┌────────────────────┐
│ RECONSTRUCTING_CAS │
└───────┬────────────┘
        │
        ▼
┌──────────────────┐
│  RECONCILING_DB  │
└───────┬──────────┘
        │
        ▼
┌──────────────────┐
│ VERIFYING_AUDIT  │
└───────┬──────────┘
        │
        ├─────────────────────────────┐
        ▼                             ▼
┌──────────────────────┐        ┌───────────┐
│ REPLAYING_GENERATION │        │ RECOVERED │ (Terminal verified state)
└───────┬──────────────┘        └───────────┘
        │                             ▲
        └─────────────────────────────┘
```

- **Transitions:** ทุกขั้นตอนมีทางออกไปยัง `FAILED` หรือ `QUARANTINED` เมื่อตรวจพบข้อมูลเสียหายที่กู้ไม่ได้
- **Terminal States:** `RECOVERED`, `FAILED`, `QUARANTINED`
- **[REQ-S08-007]** สถานะ `RECOVERED` ต้องคืน verified resume target (`RUNNING`, `PAUSED` หรือ `STOPPED`)

---

## 4. Governance State Machine (12 States)

ควบคุมการอนุมัติและปรับเปลี่ยนสเปก/นโยบาย (Governed Specification Change)

```text
DRAFT -> IMPACT_ANALYZED -> AUTHORITY_CHECKED -> SAFETY_REVIEWED 
-> TRACEABILITY_UPDATED -> APPROVED -> VERSIONED -> EVIDENCE_INVALIDATED 
-> GATES_RUNNING -> ACCEPTED | REJECTED | WITHDRAWN
```

- **Terminal States:** `ACCEPTED`, `REJECTED`, `WITHDRAWN`
- **[REQ-S08-010]** ผู้เสนอการแก้ไข (Author) ห้ามเป็นผู้อนุมัติคนเดียว (Sole Approver) สำหรับการแก้ไขที่มีผลต่อระดับ L0–L3

---

## 5. Deployment State Machine (8 States)

ควบคุมการส่งออกและการโปรโมต Candidate ไปใช้งานจริง

```text
ARCHIVED -> STAGED -> CANARY -> VALIDATED -> APPROVED -> ACTIVE -> SUPERSEDED | ROLLED_BACK
```

- **Terminal States:** `SUPERSEDED`, `ROLLED_BACK`
- **[REQ-S19-001]** หากพบความผิดปกติระหว่าง `CANARY` (เช่น Error rate $> 1.0\%$, Latency regression $> 15\%$, Crash count $> 0$) ให้ตัดสถานะไปที่ `ROLLED_BACK` ทันที

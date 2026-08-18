# Distributed P2P Evolutionary Swarm & Gossip Island Migration

> **Subsystem:** Decentralized P2P Scaling & Swarm Consensus  
> **Authority Level:** NARRATIVE — rank 4 in `spec/authority.yaml` document_precedence. Explains the canonical sources; must not contradict them.  
> **Scope:** Integrated Core v1 Architecture

---

## 1. Decentralized Island Topology

ในสถาปัตยกรรม **Distributed P2P Swarm** แต่ละเครื่องจะทำหน้าที่เป็น Island Node ที่รัน Evolution Loop ของตนเองอย่างเป็นอิสระ:

```text
┌──────────────┐          Gossip Protocol         ┌──────────────┐
│ Island Node A├─────────────────────────────────►│ Island Node B│
│ (Local Pop)  │◄─────────────────────────────────┤ (Local Pop)  │
└──────┬───────┘        Pareto Elite Exchange     └──────┬───────┘
       │                                                 │
       │                   ┌──────────────┐              │
       └──────────────────►│ Island Node C│◄─────────────┘
                           │ (Local Pop)  │
                           └──────────────┘
```

---

## 2. Elite Migration & Byzantine Sandbox Verification

1. **Periodic Migration:** ทุกๆ $M_{\text{interval}} = 10\text{ Generations}$ โหนดจะส่ง Candidate บน **Pareto Front ลำดับที่ 1 ($F_1$)** ไปยังโหนดข้างเคียงผ่าน GossipSub Protocol
2. **Byzantine Fault-Tolerant Verification:** โหนดผู้รับ **ห้ามนำ Candidate ที่ได้รับเข้าสู่ประชากรโดยตรง** ต้องส่ง Candidate เข้า Sandbox ของตนเองเพื่อรัน Test Suite และวัดผลใหม่ เพื่อป้องกันโหนดที่ไม่หวังดีส่ง Malicious Payload เข้าสู่ Swarm

# Domain 18: Distributed P2P Swarm & Gossip Island Migration

> **Domain Index:** `DOMAIN-18`  
> **Engineering Scope:** `DIM-171` .. `DIM-180`  
> **Mathematical Equations:** `EQ-171` .. `EQ-180`  
> **Authority Level:** OVERVIEW — rank 5 in `spec/authority.yaml` document_precedence. Pointer material only.  
> **Scope:** MASTER SPECIFICATION

---

## 1. Executive Summary & Domain Scope

Domain 18 กำหนดการประมวลผลวิวัฒนาการแบบกระจายศูนย์บน **P2P Island Swarm Topology** โดยใช้ **GossipSub Protocol**, การแลกเปลี่ยน Pareto Elites, **Byzantine Fault Tolerance Bound ($N \ge 3f + 1$)**, **Graph Algebraic Connectivity ($\lambda_2$)**, และการ Re-verify Candidate ในเครื่องปลายทาง.

---

## 2. The 10 Engineering Dimensions & Mathematical Formulations

```text
┌──────────┬──────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Dim ID   │ Eq ID    │ Engineering Dimension Title               │ Canonical Mathematical Equation                             │
├──────────┼──────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ DIM-171  │ EQ-171   │ P2P Island Swarm Migration Rate Bound     │ M_rate = N_immigrants / N_pop <= 0.10                       │
│ DIM-172  │ EQ-172   │ GossipSub Peer Discovery Fanout Bound     │ D_fanout >= ceil(ln(N_nodes))                               │
│ DIM-173  │ EQ-173   │ Periodic Elite Migration Generation Interval│ g mod M_interval === 0                                    │
│ DIM-174  │ EQ-174   │ Byzantine Fault Tolerance Consensus Bound │ N >= 3f + 1 <=> f <= floor((N - 1) / 3)                     │
│ DIM-175  │ EQ-175   │ Graph Algebraic Connectivity (λ_2) Metric │ lambda_2(L) = min_{x perp 1, ||x||=1} x^T L x               │
│ DIM-176  │ EQ-176   │ Swarm Global Pareto Frontier Consensus    │ F_global = NonDominated(Union_{k=1}^K F_{local, k})         │
│ DIM-177  │ EQ-177   │ Bandwidth-Optimized Compressed Migration  │ Size(Z_gzip(Candidate)) <= 4096 bytes                       │
│ DIM-178  │ EQ-178   │ Malicious Peer Node Reputation Score      │ S_peer = (N_valid - 5 * N_malicious) / N_total              │
│ DIM-179  │ EQ-179   │ Heterogeneous Workload Proportional Split │ N_k = N_total * (BFLOPS_k / sum BFLOPS_j)                   │
│ DIM-180  │ EQ-180   │ Swarm Audit Hash XOR Synchronizer Check   │ H_swarm = bigoplus_{k=1}^K H_{node_k}                       │
└──────────┴──────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Specifications & Implementation Constraints (All 10 Dimensions)

### `DIM-171` / `EQ-171`: P2P Island Swarm Migration Rate Bound
- จำกัดอัตราการย้ายถิ่นฐานของประชากรข้าม Island ไม่เกิน 10% เพื่อรักษาความหลากหลายในท้องถิ่น:
  $$M_{\text{rate}} = \frac{N_{\text{immigrants}}}{N_{\text{pop}}} \le 0.10$$

### `DIM-172` / `EQ-172`: GossipSub Peer Discovery Fanout Bound
- การเชื่อมต่อ Peer ต้องมี Fanout อย่างน้อย $\lceil \ln(N_{\text{nodes}}) \rceil$:
  $$D_{\text{fanout}} \ge \lceil \ln(N_{\text{nodes}}) \rceil$$

### `DIM-173` / `EQ-173`: Periodic Elite Migration Generation Interval
- การส่งต่อ Elite Candidate จะกระทำทุกๆ $M_{\text{interval}}$ รุ่น:
  $$g \pmod{M_{\text{interval}}} \equiv 0$$

### `DIM-174` / `EQ-174`: Byzantine Fault Tolerance Bound
- ขอบเขตความปลอดภัยในการทนทานต่อโหนดไม่หวังดีใน Swarm:
  $$N \ge 3f + 1 \iff f \le \left\lfloor \frac{N - 1}{3} \right\rfloor$$

### `DIM-175` / `EQ-175`: Graph Algebraic Connectivity ($\lambda_2$) Metric
- การเชื่อมต่อของเครือข่าย Swarm วัดผ่านค่า Eigenvalue ลำดับที่ 2 ของ Graph Laplacian:
  $$\lambda_2(L) = \min_{x \perp \mathbf{1}, \|x\|=1} x^T L x$$

### `DIM-176` / `EQ-176`: Swarm Pareto Frontier Consensus
- การรวม Front ระดับโลกจากทุกโหนด:
  $$F_{\text{global}} = \text{NonDominated}\left(\bigcup_{k=1}^K F_{\text{local}, k}\right)$$

### `DIM-177` / `EQ-177`: Bandwidth-Optimized Compressed Migration
- ขนาดของ Payload ที่ส่งข้ามเครือข่ายต้องถูกบีบอัดไม่เกิน 4KB:
  $$\text{Size}(Z_{\text{gzip}}(\text{Candidate})) \le 4096 \quad \text{bytes}$$

### `DIM-178` / `EQ-178`: Malicious Peer Node Reputation Score
- ตัดสิทธิ์โหนดที่ส่ง Candidate อันตราย:
  $$S_{\text{peer}} = \frac{N_{\text{valid}} - 5 N_{\text{malicious}}}{N_{\text{total}}}$$

### `DIM-179` / `EQ-179`: Heterogeneous Workload Proportional Split
- จัดสรรภาระงานตามกำลังการประมวลผล (BFLOPS) ของแต่ละโหนด:
  $$N_k = N_{\text{total}} \cdot \frac{\text{BFLOPS}_k}{\sum \text{BFLOPS}_j}$$

### `DIM-180` / `EQ-180`: Swarm Audit Hash XOR Synchronizer Check
- การตรวจสอบความสอดคล้องของ State ทั้งหมดใน Swarm:
  $$H_{\text{swarm}} = \bigoplus_{k=1}^K H_{\text{node}_k}$$

---

## 4. Verification Assertions & Conformance Tests

1. **Test `TC-D18-01` [Byzantine Rejection]:** โหนดจำลองส่ง Malicious Candidate เข้ามา โหนดปลายทางต้องส่งเข้า Sandbox และปฏิเสธพร้อมตัดคะแนน Reputation
2. **Test `TC-D18-02` [Gossip Propagation]:** ทดสอบส่ง Elite Candidate ข้าม 10 โหนด ตรวจสอบว่ากระจายตัวครบทุกโหนดภายในเวลาที่กำหนด
3. **Test `TC-D18-03` [Bandwidth Compression Limit]:** ตรวจสอบว่าทุก Candidate Migration Packet มีขนาดไม่เกิน 4KB
4. **Test `TC-D18-04` [Global Pareto Consensus]:** ยืนยันว่า $F_{\text{global}}$ รวมตัวแทนที่เหนือกว่าจากทุกเกาะได้อย่างถูกต้อง

# Content-Addressed Storage (CAS) Engine Specification

> **Authority Level:** NORMATIVE STORAGE SPECIFICATION (L5 Authority)  
> **Target Subsystem:** CAS Storage Subsystem (`.evolution/cas/`)  
> **Governing Equations:** `EQ-261` (CAS 2-Tier Sharding), `EQ-262` (Atomic Temp-Fsync-Rename), `EQ-263` (Zero Torn Reads)

---

## 1. Directory Structure & 2-Tier Sharding Hierarchy

CAS จัดเก็บ Payload ของ Source Files, Artifacts, Test Evidence, และ Manifests โดยใช้ **SHA-256 Digest (64 Hex Chars)** แบ่งโฟลเดอร์ 2 ระดับ:

```text
.evolution/cas/
├── tmp/                          <-- Temporary files before fsync and rename
│   ├── .tmp_1708272000_12345
│   └── .tmp_1708272001_67890
├── 0a/                           <-- First 2 hex characters of hash
│   ├── 0a1b2c3d4e5f... (Blob file, chmod 0444 read-only)
│   └── 0afe89d0124a...
├── 4f/
│   └── 4f88921a9c3d...
└── ff/
    └── ffa9012bc45e...
```

---

## 2. The Atomic Temp-Fsync-Rename Pipeline (Zero Torn Reads)

เพื่อป้องกันปัญหาไฟล์พังหรืออ่านได้ข้อมูลครึ่งๆ กลางๆ (Torn Reads) จากการตัดไฟหรือระบบดับกลางคัน กระบวนการเขียน Blob ลง CAS ต้องปฏิบัติตามลำดับ 5 ขั้นตอนนี้อย่างเคร่งครัด:

```text
  [1. Compute SHA-256] ──► [2. Write to tmp/ file] ──► [3. POSIX fsync(fd)]
                                                              │
  [5. POSIX fsync(parent_dir)] ◄── [4. Atomic POSIX rename()] ◄┘
```

### 2.1 Concrete Implementation Rules
1. **Write to Staging:** เขียนข้อมูลลงไฟล์ชั่วคราว `.evolution/cas/tmp/.tmp_<pid>_<timestamp>_<uuid>`
2. **Flush to Disk:** เรียก `os.fsync(fd)` เพื่อบังคับให้ Disk Controller เขียนข้อมูลลง Physical Storage จริง
3. **Atomic Rename:** เรียก `os.rename(tmp_path, target_path)` ซึ่งเป็น Atomic Operation ในระดับเคอร์เนล POSIX Filesystem
4. **Directory Sync:** เรียก `os.fsync(parent_dir_fd)` เพื่อให้ Directory Entry ถูกบันทึกคงทน
5. **Set Read-Only:** กำหนด Permission เป็น `chmod 0444` (Read-only) ทันทีหลังเขียนเสร็จ เพื่อป้องกันการแก้ไข

---

## 3. Garbage Collection & Retention Math

Blob ใน CAS จะถูกลบออกก็ต่อเมื่อไม่มี Foreign Key หรือ Reference ใดๆ จาก SQLite Database และ Lineage DAG:
$$\text{GC}(b) \iff b \notin \text{ReferencedBlobs}(\text{DB} \cup \text{Lineage})$$

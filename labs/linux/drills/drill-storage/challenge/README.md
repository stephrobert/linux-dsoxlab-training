# Drill — partitions, LVM and swap

**Format**: 5 tasks, 100 points, 25 minutes. **No hints.**
The disk **`/dev/vdb`** is attached and **blank**.

```bash
dsoxlab check drill-storage                  # AlmaLinux (default)
dsoxlab check drill-storage --target ubuntu  # Ubuntu
```

---

### Task 1 — Partition (20 pts)

On `/dev/vdb`, create a **GPT** table and two partitions: **`/dev/vdb1` of
2 GiB** and **`/dev/vdb2` of 1 GiB**.

### Task 2 — The LVM stack (20 pts)

Make `/dev/vdb1` a physical volume, in the volume group **`vgdrill`**. Create
the logical volume **`lvdata`** of **1 GiB**, formatted **XFS**.

### Task 3 — Persistent mount (20 pts)

Mount `lvdata` on **`/mnt/data`**, persistently, **by UUID** — not by device
path.

### Task 4 — Swap (20 pts)

Add **128 MiB** of swap as the file **`/swapfile`**, active and persistent.

### Task 5 — Extend online (20 pts)

Extend **`lvdata` to 1.5 GiB**. The filesystem must reflect the new size
**without unmounting** — an extended volume whose filesystem did not follow
gives you no usable space at all.

---

## Validate

```bash
dsoxlab check drill-storage
```

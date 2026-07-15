# Challenge — l1-03 : Inventory your machine's resources

Work in **`challenge/work/`** — the `vm-info.txt` file was created there by
`dsoxlab run`.

---

## Mission

When facing a fresh machine, an administrator's first reflex is to know
**what it has**. Inventory your machine's resources and record four real values
in `vm-info.txt`:

1. `CPU_COUNT` — the number of processors, via `nproc`.
2. `ARCH` — the architecture, via `uname -m`.
3. `MEM_TOTAL_KB` — the total memory in kB, in `/proc/meminfo`.
4. `BLOCK_DEVICE` — the name of **one** real disk, via `lsblk`.

## Constraints

- Each value must be the **actual value of your machine**: validation compares
  it to the real system state. A made-up value fails.
- All `VOTRE_RÉPONSE_ICI` placeholders must be replaced.

## Useful commands

```bash
nproc
uname -m
grep MemTotal /proc/meminfo
lsblk -dno NAME
```

## Validation

```bash
dsoxlab check l1-prepare-vm
```

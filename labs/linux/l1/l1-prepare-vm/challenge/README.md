# Taking inventory of a machine you just met

## The situation

Faced with a new machine, an administrator's first reflex is not to install it:
it is to know **what it has**. How many processors, which architecture, how much
memory, which disks. That is what decides what can run on it, and it is the
first thing you will be asked the day you open a ticket.

This lab has you write that identity card for your own machine. Every value is
checked against the real state of the system: a plausible but invented value
fails.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/discover-linux/install-vm/

## Inventory your machine's resources

Work in **`challenge/work/`** — the `vm-info.txt` file was created there by
`dsoxlab run`.

---

### Mission

When facing a fresh machine, an administrator's first reflex is to know
**what it has**. Inventory your machine's resources and record four real values
in `vm-info.txt`:

1. `CPU_COUNT` — the number of processors, via `nproc`.
2. `ARCH` — the architecture, via `uname -m`.
3. `MEM_TOTAL_KB` — the total memory in kB, in `/proc/meminfo`.
4. `BLOCK_DEVICE` — the name of **one** real disk, via `lsblk`.

### Constraints

- Each value must be the **actual value of your machine**: validation compares
  it to the real system state. A made-up value fails.
- All `<value>` placeholders must be replaced.

### Useful commands

```bash
nproc
uname -m
grep MemTotal /proc/meminfo
lsblk -dno NAME
```

### Validation

```bash
dsoxlab check l1-prepare-vm
```

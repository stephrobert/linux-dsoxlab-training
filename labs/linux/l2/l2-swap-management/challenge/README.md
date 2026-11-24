# Add swap to a memory-tight server

## The situation

You are the admin on **alma-rhcsa-1.lab**. A batch job occasionally spikes
memory and the kernel OOM killer has already terminated it twice. Until the
job is fixed, you need a **safety valve**: a small swap area that absorbs the
peaks, without letting the box swap aggressively.

Two requirements go together: that valve must still be there on the next boot,
and the kernel must only fall back to it as a last resort.

The full method is in the companion guide:
https://www.stephane-robert.info/en/docs/linux/storage/swap/

## Add and manage swap space

### Mission

On **alma-rhcsa-1.lab**, add a **256 MiB swap file** to the system, make it
secure and persistent, and tune the kernel's swap behaviour.

You must:

1. Create a swap file `/swapfile` of **256 MiB**, owned by `root:root`, mode **0600**.
2. Format it (`mkswap`) and **activate** it (`swapon`).
3. Make it **persistent** across reboots via `/etc/fstab`.
4. Set **`vm.swappiness = 10`** durably (drop-in in `/etc/sysctl.d/`).

### Constraints

- The swap file **must** be mode `0600` (it holds memory pages).
- The fstab entry must reference `/swapfile` with type `swap`.
- `vm.swappiness` must read `10` (`sysctl -n vm.swappiness`).

### Useful approach

The steps follow from the companion guide linked in the course's
`## Reminder`. If you get stuck, `dsoxlab hint` spells them out, at the
stated cost.

### Validation

```bash
dsoxlab check l2-swap-management
```

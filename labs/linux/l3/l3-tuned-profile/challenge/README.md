# Tune the box for throughput

## The situation

This machine runs data-heavy batch work but sits on the default **`balanced`**
tuned profile. Switch it to a profile built for **throughput**, so the kernel
knobs (CPU governor, I/O, VM) are set for sustained load — and make it survive a
reboot.

The point: `tuned` bundles dozens of kernel and sysfs settings into named
profiles, one per broad kind of workload. The chosen profile is recorded on disk,
and that is what makes it hold across reboots. What's left is picking the right
one and switching to it.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/tuned/

## What is asked

### Mission

Switch the active tuned profile to `throughput-performance`, persistently.

### Goal (expected state)

1. The `tuned` service is running.
2. `tuned-adm active` → **`throughput-performance`**.
3. `/etc/tuned/active_profile` contains `throughput-performance` (persistence).

### Constraints

- `tuned-adm profile throughput-performance`. Validation reads the **actually
  active profile**, not the command.

### Validation

```bash
dsoxlab check l3-tuned-profile
```

# Challenge — l2-disk-space-troubleshoot

## Mission

`/srv/data` is almost full on the VM. Diagnose and reclaim space.

## Goal (expected state)

1. `/srv/data` is **still mounted**.
2. Its usage is **under 50%**.
3. The legitimate file `/srv/data/app.log` is **kept**.

## Constraints

- Diagnose with `df -h` then `du -h --max-depth=1 /srv/data`. Delete only the
  superfluous (the cache), not the legitimate data; do not unmount/reformat.
- Validation reads the **real state** (mount, `df` usage, presence of app.log).

## Validation

```bash
dsoxlab check l2-disk-space-troubleshoot
```

# Challenge — lfcs-package-apt

## Mission

Install and pin a Debian package with apt.

## Goal (expected state)

1. `tree` is installed.
2. `tree` is on hold (`apt-mark showhold` lists it).
3. `dpkg -S /usr/bin/tree` resolves to `tree`.

## Constraints

- Use `apt`/`dpkg` (Debian tooling), not `dnf`.
- Validation reads the package status and the hold list.

## Validation

```bash
dsoxlab check lfcs-package-apt
```

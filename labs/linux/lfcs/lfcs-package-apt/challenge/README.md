# Debian package management with apt

## The situation

On a Debian/Ubuntu system, packages are handled by **apt** (high level) and
**dpkg** (low level). You need to install a tool, then **pin** it so a system
upgrade won't change it — and be able to say which package a given file came from.

The point: apt manages packages with their dependencies and can freeze a
package's version so an upgrade leaves it alone; dpkg, underneath, can tell which
package a file belongs to. These are the Debian counterparts of `dnf` and `rpm`.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/maintain/packages/apt/

## What is asked

### Mission

Install and pin a Debian package with apt.

### Goal (expected state)

1. `tree` is installed.
2. `tree` is on hold (`apt-mark showhold` lists it).
3. `dpkg -S /usr/bin/tree` resolves to `tree`.

### Constraints

- Use `apt`/`dpkg` (Debian tooling), not `dnf`.
- Validation reads the package status and the hold list.

### Validation

```bash
dsoxlab check lfcs-package-apt
```

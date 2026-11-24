# Bring the machine to a target software state

## The situation

Managing software is daily work: install what a service needs, remove what
shouldn't be there, and be able to prove the result. Right now `zip` is installed
but unwanted, and `tree` is missing but needed.

The point: the package manager changes the machine's software state and resolves
dependencies along the way; the RPM database keeps the record. The tests read
that database, so the machine's real state is what counts, not the command you
typed.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/maintain/packages/dnf/

## What is asked

### Mission

Bring the machine to the target software state.

### Goal (expected state)

1. The **`tree`** package is **installed**.
2. The **`zip`** package is **removed**.
3. The `tree` command is available.

### Constraints

- `dnf install` / `dnf remove` ; check with `rpm -q`. Validation reads the
  **RPM database** (real state), not the command typed.

### Validation

```bash
dsoxlab check l2-package-management
```

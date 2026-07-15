# Challenge — l2-package-management

## Mission

Bring the machine to the target software state.

## Goal (expected state)

1. The **`tree`** package is **installed**.
2. The **`zip`** package is **removed**.
3. The `tree` command is available.

## Constraints

- `dnf install` / `dnf remove` ; check with `rpm -q`. Validation reads the
  **RPM database** (real state), not the command typed.

## Validation

```bash
dsoxlab check l2-package-management
```

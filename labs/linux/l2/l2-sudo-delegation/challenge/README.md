# Challenge — l2-sudo-delegation

## Mission

Delegate a restricted sudo to the `operators` group (of which `ops` is a member).

## Goal (expected state)

1. A drop-in `/etc/sudoers.d/operators` exists.
2. `%operators` can run **`/usr/bin/systemctl` only**, with **`NOPASSWD`**.
3. The sudoers syntax stays **valid** (`visudo -c` returns 0).
4. No full sudo for ops (least privilege).

## Constraints

- Edit via `visudo -f /etc/sudoers.d/operators` (validated on save),
  mode `0440`. Validation reads the **effective policy** (`sudo -l -U ops`).

## Validation

```bash
dsoxlab check l2-sudo-delegation
```

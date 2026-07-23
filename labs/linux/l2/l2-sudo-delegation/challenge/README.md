# Challenge — l2-sudo-delegation

## Mission

Delegate a restricted sudo to the `operators` group (of which `ops` is a member).

## Goal (expected state)

1. A drop-in `/etc/sudoers.d/operators` exists.
2. `%operators` can run **`/usr/bin/systemctl` only**, with **`NOPASSWD`**.
3. The sudoers syntax stays **valid** (`visudo -c` returns 0).
4. No full sudo for ops (least privilege).

## Constraints

- Edit via `visudo -f /etc/sudoers.d/operators`: it validates the syntax on
  save, but it does **not** set the expected permissions. It leaves the file at
  `0640`, and `visudo -c` then rejects the whole set (`bad permissions, should
  be mode 0440`) even though the rule works. So finish with
  `chmod 0440 /etc/sudoers.d/operators`.
- Validation reads the **effective policy** (`sudo -l -U ops`).

## Validation

```bash
dsoxlab check l2-sudo-delegation
```

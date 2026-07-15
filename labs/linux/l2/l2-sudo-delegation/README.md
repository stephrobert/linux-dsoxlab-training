# Lab — delegate limited sudo

> Prepare: `dsoxlab provision` then `dsoxlab run l2-sudo-delegation`

## Recap

[**sudo on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/)

Put sudo policy in `/etc/sudoers.d/` drop-ins (mode `0440`). A rule reads
`who where=(as-whom) commands`; `%group` targets a group, `NOPASSWD:` drops the
password prompt, and listing explicit commands is least privilege. **Always**
validate with `visudo -cf <file>` — a syntax error can break all sudo.
`sudo -l -U <user>` shows the effective policy.

## Objectives

- drop-in `/etc/sudoers.d/operators`;
- `%operators` may run **only** `/usr/bin/systemctl`, `NOPASSWD`;
- sudoers stays syntactically valid (`visudo -c`).

## Validate

```bash
dsoxlab check l2-sudo-delegation
```

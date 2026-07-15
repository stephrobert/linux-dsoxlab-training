# Lab — password aging & complexity

> Prepare: `dsoxlab provision` then `dsoxlab run l2-password-policy`

## Recap

[**Users & groups on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`chage -M <max> -m <min> -W <warn> <user>` sets per-account aging (`chage -l`
shows it). `/etc/login.defs` holds `PASS_MAX_DAYS` and friends — the defaults
applied to newly created accounts. `/etc/security/pwquality.conf` enforces
complexity, e.g. `minlen` for the minimum length.

## Objectives

- `bob`: max 60, min 7, warn 7 (`chage`);
- `PASS_MAX_DAYS 60` in `/etc/login.defs`;
- `minlen = 12` in `/etc/security/pwquality.conf`.

## Validate

```bash
dsoxlab check l2-password-policy
```

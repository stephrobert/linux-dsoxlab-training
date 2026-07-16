# Lab — manage an AppArmor profile

> Prepare: `dsoxlab provision` then `dsoxlab run lfcs-apparmor`

## Recap

[**AppArmor on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/)

AppArmor confines programs with per-binary profiles. `aa-status` lists loaded
profiles and their mode; `aa-complain <profile>` switches one to learning mode
(logs, doesn't block), `aa-enforce` back to enforcing, `aa-disable` unloads it.
It's the Debian counterpart to SELinux, but per profile.

## Objectives

- AppArmor is active with profiles loaded;
- the `ping` profile is in `complain` mode (`aa-status`).

## Validate

```bash
dsoxlab check lfcs-apparmor
```

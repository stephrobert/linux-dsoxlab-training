# Lab — tuned performance profile

> Prepare: `dsoxlab provision` then `dsoxlab run l3-tuned-profile`

## Recap

[**tuned on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/)

`tuned` applies a named bundle of kernel/sysfs tunings. `tuned-adm list` shows
available profiles, `tuned-adm active` the current one, `tuned-adm profile
<name>` switches. The active choice is saved in `/etc/tuned/active_profile`, so it
persists. The `tuned` service must run.

## Objectives

- active profile = `throughput-performance`;
- persisted in `/etc/tuned/active_profile`.

## Validate

```bash
dsoxlab check l3-tuned-profile
```

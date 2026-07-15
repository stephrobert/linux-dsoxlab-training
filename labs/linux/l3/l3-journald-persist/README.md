# Lab — persistent journald

> Prepare: `dsoxlab provision` then `dsoxlab run l3-journald-persist`

## Recap

[**systemd journals on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/)

journald stores logs in `/run/log/journal` (volatile) by default. With
`Storage=persistent` (in `journald.conf` or a `journald.conf.d/` drop-in) **and**
a `/var/log/journal` directory, logs go to disk and survive reboots. Restart
`systemd-journald` and `journalctl --flush` to move them. `journalctl -b -1`
reads the previous boot.

## Objectives

- `Storage=persistent` in journald config;
- `/var/log/journal` exists;
- a real `.journal` file is written under it.

## Validate

```bash
dsoxlab check l3-journald-persist
```

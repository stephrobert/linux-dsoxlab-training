# Challenge — l3-journald-persist

## Mission

The systemd journal is volatile (lost on reboot). Make it persistent.

## Goal (expected state)

1. `/var/log/journal` exists (directory).
2. The journald config declares **`Storage=persistent`**.
3. A `.journal` file is written under `/var/log/journal` (journald has switched over).

## Constraints

- `Storage=persistent` (journald.conf or drop-in), `mkdir /var/log/journal`,
  then `systemctl restart systemd-journald` + `journalctl --flush`. Validation
  reads the **actual state** (config, directory, journal file).

## Validation

```bash
dsoxlab check l3-journald-persist
```

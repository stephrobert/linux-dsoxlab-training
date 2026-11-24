# Keep the logs after a reboot

## The situation

On this machine the journal is **volatile**: everything `journalctl` shows is
lost on reboot, which is a nightmare when you need to investigate why a server
went down. Make the systemd journal **persistent**.

The point: by default journald writes to a volatile location, wiped at every
boot. Switching to storage that survives a reboot does not come down to a single
setting: the configuration has to allow it, and the destination has to be ready
to hold the journal.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/systemd/journald/

## What is asked

### Mission

The systemd journal is volatile (lost on reboot). Make it persistent.

### Goal (expected state)

1. `/var/log/journal` exists (directory).
2. The journald config declares **`Storage=persistent`**.
3. A `.journal` file is written under `/var/log/journal` (journald has switched over).

### Constraints

- `Storage=persistent` (journald.conf or drop-in), `mkdir /var/log/journal`,
  then `systemctl restart systemd-journald` + `journalctl --flush`. Validation
  reads the **actual state** (config, directory, journal file).

### Validation

```bash
dsoxlab check l3-journald-persist
```

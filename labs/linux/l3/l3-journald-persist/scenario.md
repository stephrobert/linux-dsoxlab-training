# Context — keep the logs after a reboot

On this machine the journal is **volatile**: everything `journalctl` shows is
lost on reboot, which is a nightmare when you need to investigate why a server
went down. Make the systemd journal **persistent**.

Your mission, on the VM:

1. Set **`Storage=persistent`** for journald (in `/etc/systemd/journald.conf` or,
   cleaner, a drop-in under `/etc/systemd/journald.conf.d/`).
2. Create the **`/var/log/journal`** directory.
3. **Restart** `systemd-journald` (and `journalctl --flush`) so it starts writing
   to disk.

The point: journald keeps logs in `/run` (volatile) unless `/var/log/journal`
exists and `Storage` allows it; `persistent` forces on-disk storage that survives
reboots. `journalctl --disk-usage` and `journalctl -b -1` (previous boot) confirm
it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/

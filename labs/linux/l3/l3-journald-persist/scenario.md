# Context — keep the logs after a reboot

On this machine the journal is **volatile**: everything `journalctl` shows is
lost on reboot, which is a nightmare when you need to investigate why a server
went down. Make the systemd journal **persistent**.

The point: by default journald writes to a volatile location, wiped at every
boot. Switching to storage that survives a reboot does not come down to a single
setting: the configuration has to allow it, and the destination has to be ready
to hold the journal.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/

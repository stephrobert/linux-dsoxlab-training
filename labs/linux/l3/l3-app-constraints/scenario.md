# Context — raise an application's resource ceiling

The service running as **`appuser`** opens thousands of files and keeps hitting
the default open-files limit. You must raise its `nofile` limit — and make it
stick for every new session, not just this shell.

Your mission, on the VM — for user `appuser`:

1. Set the **soft** open-files limit (`nofile`) to **4096**.
2. Set the **hard** limit to **8192**.
3. Do it in `/etc/security/limits.d/` so it applies at every login (via
   `pam_limits`).

The point: `ulimit` shows/sets the current shell's limits, but the durable policy
lives in `/etc/security/limits.conf` and `/etc/security/limits.d/*.conf`
(`<who> <soft|hard> <item> <value>`). A soft limit is the default, the hard limit
is the ceiling a user can raise up to. Check with
`su - appuser -c 'ulimit -Sn'`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/

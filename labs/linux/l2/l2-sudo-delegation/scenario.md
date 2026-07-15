# Context — hand out just enough sudo

The operations team needs to restart services, but they must **not** get full
root. This is delegation with least privilege: a `/etc/sudoers.d` drop-in that
allows the `operators` group to run `systemctl` — and only that — without a
password.

Your mission, on the VM:

1. Create a drop-in `/etc/sudoers.d/operators`.
2. Grant the **`operators`** group `NOPASSWD` sudo for **`/usr/bin/systemctl`
   only** (not `ALL`).
3. **Validate the syntax** before it takes effect — a broken sudoers file can
   lock out *all* sudo. Use `visudo -cf <file>`.

The point: sudoers drop-ins keep policy modular; `%group` targets a group;
limiting the command list is least privilege; and `visudo` validation is
non-negotiable because a syntax error is catastrophic.

`sudo -l -U ops` shows what the user is actually allowed.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/

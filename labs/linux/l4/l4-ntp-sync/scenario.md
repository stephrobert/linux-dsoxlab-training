# Context — put the clock back in sync

This host drifted: its timezone is wrong, NTP is off and `chronyd` isn't even
running. Logs get confusing timestamps and TLS handshakes start failing when the
clock is off. Bring it back — and make it hold across a reboot.

Your mission, on the VM:

1. Set the timezone to **`Europe/Paris`** (`timedatectl set-timezone`).
2. Turn **NTP on** (`timedatectl set-ntp true`).
3. **Enable and start** `chronyd` so it survives a reboot
   (`systemctl enable --now chronyd`).

The point: `chronyd` is the NTP client on RHEL; `timedatectl` drives the
timezone and the NTP toggle. A service that runs now but isn't `enabled` is gone
after the next reboot — the classic RHCSA trap.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/reseau/chrony/

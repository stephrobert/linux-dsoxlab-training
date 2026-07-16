# Context — AppArmor, Debian's mandatory access control

Where RHEL uses SELinux, Debian/Ubuntu uses **AppArmor**: per-program profiles
that confine what a binary can do. A profile runs in **enforce** (violations
blocked) or **complain** (violations only logged — the learning mode you use while
tuning a profile).

Your mission, on the Ubuntu VM:

1. Put the profile for the `ping` binary (`/etc/apparmor.d/bin.ping`) into
   **complain** mode: `sudo aa-complain /etc/apparmor.d/bin.ping`.
2. Confirm with **`sudo aa-status`** — `ping` should be listed under the profiles
   in complain mode.

The point: `aa-status` shows loaded profiles and their mode; `aa-complain`
switches one to learning mode, `aa-enforce` back to enforcing, `aa-disable` unloads
it. It's AppArmor's answer to SELinux's enforcing/permissive — but per profile,
not global.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/

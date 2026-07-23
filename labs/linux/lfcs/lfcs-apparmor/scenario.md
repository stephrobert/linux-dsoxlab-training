# Context — AppArmor, Debian's mandatory access control

Where RHEL uses SELinux, Debian/Ubuntu uses **AppArmor**: per-program profiles
that confine what a binary can do. A profile runs in **enforce** (violations
blocked) or **complain** (violations only logged — the learning mode you use while
tuning a profile).

The point: AppArmor is driven profile by profile. You can put one profile into
learning mode, put it back into enforce, or unload it entirely, without touching
the others. It's AppArmor's answer to SELinux's enforcing/permissive — but per
program, not per machine.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/

# Context — turn a program into a managed service

A small program (`/usr/local/bin/labapp.sh`) needs to run as a proper **systemd
service**: started now, restarted on failure, and brought up automatically at
boot. Right now it has no unit at all.

The point: a unit file describes *how* to run something. What is left is getting
systemd to take that description into account, then telling "runs now" apart from
"comes back at the next boot": those are two distinct moves.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/

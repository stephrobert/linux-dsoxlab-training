# Context — turn a program into a managed service

A small program (`/usr/local/bin/labapp.sh`) needs to run as a proper **systemd
service**: started now, restarted on failure, and brought up automatically at
boot. Right now it has no unit at all.

Your mission, on the VM:

1. Write a unit `/etc/systemd/system/labapp.service` (`Type=simple`,
   `ExecStart=/usr/local/bin/labapp.sh`, a sensible `Restart=`, and an
   `[Install]` section).
2. Reload systemd (`systemctl daemon-reload`).
3. **Start and enable** it (`systemctl enable --now labapp`).

The point: a unit file describes *how* to run something; `daemon-reload` makes
systemd read a new/changed unit; `start` runs it now, `enable` wires it to a
target so it comes up on boot. `systemctl status labapp` shows the result.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/

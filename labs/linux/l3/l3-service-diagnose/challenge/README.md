# 🎯 Challenge — Diagnose and fix a service in a crash loop

## ✅ Goal

Move the `demo-crashloop` service from `failed`/`activating`
to `active` AND `enabled` on the target VM (`alma-rhcsa-1.lab` by
default), so that the fix **survives a reboot**
(RHCSA `persistence_after_reboot` criterion).

You work directly on the VM through the SSH session opened by
`dsoxlab run`. Type the diagnostic and fix commands
live — no script to write. Validation is done by
`dsoxlab check`, which runs pytest+testinfra tests.

## 🧪 Expected diagnostic method

A senior sysadmin doesn't write a ready-made recipe. They follow the
method:

1. **Confirm the crash loop**
   `systemctl status demo-crashloop.service`

2. **Find the root cause** in the system journal (first
   error message, not the last)
   `sudo journalctl -u demo-crashloop.service -b --no-pager | head -30`

3. **Read the contract** the binary imposes
   `sudo systemctl cat demo-crashloop.service`
   `sudo cat /usr/local/bin/demo-crashloop`

4. **Apply the durable fix** (the service must be `active` AND
   `enabled` to survive a reboot)

5. **Verify**
   `systemctl is-active demo-crashloop.service`
   `systemctl is-enabled demo-crashloop.service`

## 🧩 Pitfalls to avoid

- **Do not disable SELinux** or `firewalld` to silence the
  problem — the service is failing for a specific reason.
- **Do not `chmod 777`** system config files. The right
  mode is `0644`, owner `root:root`.
- **A `systemctl restart`** is enough (no need for `daemon-reload`
  here: you're changing the app config, not the unit file).
- **`enabled` is different from `active`**: a service can be
  `active` but not `enabled` (it won't restart after a reboot).

## 🚀 Launch

You're already on the VM if you just ran `dsoxlab run`. Otherwise:

```bash
dsoxlab ssh alma-rhcsa-1
```

## 🧪 Automated validation

When you think you've solved the problem (from your host, not from
the VM):

```bash
dsoxlab check depanner-service-crash-loop
```

The test checks on the target VM:

- The file `/etc/demo-crashloop/config.yml` exists with mode `0644`
  and `root:root`.
- It contains a `port: <number>` line.
- `systemctl is-active demo-crashloop.service` returns `active`.
- `systemctl is-enabled demo-crashloop.service` returns `enabled`
  (RHCSA persistence_after_reboot criterion).
- The recent journal no longer contains the initial error pattern.

## 🧹 Reset

If you want to restart the diagnosis from scratch:

```bash
dsoxlab reset depanner-service-crash-loop
```

This replays `cleanup.yaml` then `setup.yaml` — the VM returns to the
initial crash-loop state, ready for a fresh diagnosis.

## 💡 Going further

- **`systemctl status` exit codes**: 0 if the service is
  `active`, 3 otherwise. Useful for a monitoring script.
- **`systemd-analyze verify <unit-file>`**: detects unit files that
  are syntactically invalid BEFORE trying to load them.
- **`journalctl --rotate`** + `--vacuum-time=1d`: manual rotation
  useful when a crash loop has saturated `/var/log/journal/` during the
  night.
- **Override drop-in** in `/etc/systemd/system/<svc>.d/override.conf`
  to modify `Restart=`, `RestartSec=`, `ExecStartPre=` without
  touching the main unit.

## 🤔 Reflection questions

1. If you found this service in a crash loop on **3 identical servers**
   in parallel (production), what strategy? Do you fix each one locally,
   or do you write an Ansible playbook?

2. How would you **prevent** this crash loop upstream? (Hints:
   `validate=` in Ansible, `systemd-analyze verify`, a declared
   `Requires=` or `ConditionPathExists=` dependency in the unit.)

3. If the service restarted correctly but exited after
   30 minutes (instead of instantly), how would you adapt your
   diagnosis? Which extra tools (`coredumpctl`,
   `systemd-analyze blame`)?

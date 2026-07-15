# Lab — recover a broken sshd config

> Prepare: `dsoxlab provision` then `dsoxlab run l3-ssh-access-recovery`

## Recap

[**Lost SSH access on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/)

sshd reads `/etc/ssh/sshd_config` and drop-ins under
`/etc/ssh/sshd_config.d/`. `sshd -t` validates the config offline — a broken one
only bites on the next reload/reboot, so **always** run `sshd -t` before
reloading. `sshd -T` dumps the effective settings. `systemctl reload sshd`
applies a valid config without dropping connections.

## Objectives

- `sshd -t` passes (invalid directive fixed);
- sshd running;
- `PermitRootLogin no` effective (`sshd -T`).

## Validate

```bash
dsoxlab check l3-ssh-access-recovery
```

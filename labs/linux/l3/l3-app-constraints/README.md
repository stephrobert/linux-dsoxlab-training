# Lab — per-user resource limits

> Prepare: `dsoxlab provision` then `dsoxlab run l3-app-constraints`

## Recap

[**Resource limits on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/)

`ulimit -n` shows a shell's open-files limit; the durable policy is in
`/etc/security/limits.conf` and `/etc/security/limits.d/*.conf`, one rule per line
`<domain> <type> <item> <value>` (e.g. `appuser hard nofile 8192`). `pam_limits`
applies them at login. The **soft** limit is the default, the **hard** limit is
the ceiling.

## Objectives

For `appuser`:

- soft `nofile` = 4096, hard `nofile` = 8192 (in `limits.d/`);
- effective in a login session (`su - appuser -c 'ulimit -Sn'`).

## Validate

```bash
dsoxlab check l3-app-constraints
```

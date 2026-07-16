# Lab — open a firewalld service permanently

> Prepare: `dsoxlab provision` then `dsoxlab run l4-firewall-persist`

## Recap

[**firewalld on the companion guide**](https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/)

`firewalld` filters by **zone** (default `public`). `firewall-cmd --add-service`
changes runtime only (lost on reload/reboot); `--permanent` writes the zone
config, and `--reload` applies permanent to runtime. Check with
`--list-services` (runtime) and `--permanent --list-services`.

Never remove `ssh` — that closes your management access.

## Objectives

- `http` is in the runtime service list;
- `http` is in the permanent service list (reboot persistence);
- `ssh` is still allowed.

## Validate

```bash
dsoxlab check l4-firewall-persist
```

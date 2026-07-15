# Lab — create a systemd service

> Prepare: `dsoxlab provision` then `dsoxlab run l3-service-create-unit`

## Recap

[**systemd services on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/)

A `.service` unit in `/etc/systemd/system/` has `[Unit]`, `[Service]`
(`Type=`, `ExecStart=`, `Restart=`) and `[Install]` (`WantedBy=`) sections. After
writing or editing it, run `systemctl daemon-reload`. `enable` links it into a
target (boot persistence); `start` runs it now; `enable --now` does both.

## Objectives

- `/etc/systemd/system/labapp.service` runs `/usr/local/bin/labapp.sh`;
- service **active** and **enabled**;
- it actually runs (`/run/labapp.status` = `running`).

## Validate

```bash
dsoxlab check l3-service-create-unit
```

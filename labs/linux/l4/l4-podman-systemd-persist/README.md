# Lab — boot-persistent container with Quadlet

> Prepare: `dsoxlab provision` then `dsoxlab run l4-podman-systemd-persist`

## Recap

[**Quadlet on the companion guide**](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/)

Quadlet turns `/etc/containers/systemd/*.container` files into systemd services
at `daemon-reload`. A `[Container]` section describes the image/command; the
`[Install] WantedBy=` section makes the generated service start at boot. The
service name is the file name + `.service` (here `weblab.service`).

## Objectives

- `/etc/containers/systemd/weblab.container` exists with an `[Install] WantedBy`;
- `weblab.service` is active;
- container `weblab` is running.

## Validate

```bash
dsoxlab check l4-podman-systemd-persist
```

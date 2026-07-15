# Lab — default boot target

> Prepare: `dsoxlab provision` then `dsoxlab run l3-boot-target`

## Recap

[**Boot & reboot on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/)

systemd boots into a **target**. `systemctl get-default` shows the default;
`systemctl set-default <target>` changes it (a symlink, persistent).
`multi-user.target` is the standard non-graphical server state;
`systemctl isolate <target>` switches at runtime without a reboot.

## Objectives

- default target = `multi-user.target` (`systemctl set-default`).

## Validate

```bash
dsoxlab check l3-boot-target
```

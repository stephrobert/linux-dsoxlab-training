# Lab — sync the clock with chrony

> Prepare: `dsoxlab provision` then `dsoxlab run l4-ntp-sync`

## Recap

[**Time synchronization with chrony on the companion guide**](https://blog.stephane-robert.info/docs/services/reseau/chrony/)

`chronyd` is the NTP client on RHEL-family systems. `timedatectl` shows and sets
the timezone (`set-timezone`) and toggles network time (`set-ntp`). A service
must be `enabled` to come back after a reboot — running is not enough.

## Objectives

- timezone is `Europe/Paris`;
- NTP is enabled (`timedatectl show -p NTP` → `yes`);
- `chronyd` is running **and** enabled.

## Validate

```bash
dsoxlab check l4-ntp-sync
```

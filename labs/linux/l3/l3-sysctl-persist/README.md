# Lab — persistent kernel hardening with sysctl

> Prepare: `dsoxlab provision` then `dsoxlab run l3-sysctl-persist`

## Recap

[**sysctl hardening on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/)

`sysctl -w key=value` changes a kernel parameter now (lost on reboot). A file in
`/etc/sysctl.d/*.conf` (`key = value` per line) makes it persistent;
`sysctl --system` reloads every config file. `sysctl -n <key>` reads the live
value.

## Objectives

Persistent in `/etc/sysctl.d/` and live:

- `net.ipv4.ip_forward = 0`;
- `net.ipv4.conf.all.accept_redirects = 0`.

## Validate

```bash
dsoxlab check l3-sysctl-persist
```

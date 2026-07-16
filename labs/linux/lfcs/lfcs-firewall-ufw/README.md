# Lab — Debian firewall with ufw

> Prepare: `dsoxlab provision` then `dsoxlab run lfcs-firewall-ufw`

## Recap

[**ufw on the companion guide**](https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/)

`ufw allow <service|port>` adds a rule; `ufw enable` turns the firewall on and
makes it persistent at boot; `ufw status` shows the rules. It's the Debian
equivalent of `firewall-cmd`. Always keep `OpenSSH` allowed before enabling.

## Objectives

- ufw is `active`;
- `http` (80/tcp) is allowed;
- `OpenSSH` is still allowed.

## Validate

```bash
dsoxlab check lfcs-firewall-ufw
```

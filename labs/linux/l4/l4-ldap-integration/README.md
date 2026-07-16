# Lab — LDAP authentication with SSSD

> Prepare: `dsoxlab provision` then `dsoxlab run l4-ldap-integration`

## Recap

[**SSSD + LDAP on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/)

A 389 Directory Server (`dc=lab,dc=local`) holds a posix user `alice`. SSSD is the
client daemon: `/etc/sssd/sssd.conf` (mode `0600`) with `id_provider = ldap` +
`ldap_uri` + `ldap_search_base` tells it where to look. `authselect select sssd
with-mkhomedir` wires NSS/PAM to SSSD. Then `getent passwd`/`id` answer from the
directory. No TLS in this lab, so it must be allowed explicitly.

The server's IP is in `/root/ldap-server.env`.

## Objectives

- `getent passwd alice` resolves the directory user (uid 10001);
- `id alice` works;
- the active authselect profile is `sssd`.

## Validate

```bash
dsoxlab check l4-ldap-integration
```

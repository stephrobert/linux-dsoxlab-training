# Context — let the directory users log in

A central **389 Directory Server** (base `dc=lab,dc=local`) holds your accounts —
including a posix user **`alice`**. This client machine doesn't know about it yet:
`getent passwd alice` returns nothing. Wire it up with **SSSD** so directory users
resolve and can authenticate. You won't create local accounts.

Your mission, on the client VM (the server's IP is in `/root/ldap-server.env`):

1. Configure **`/etc/sssd/sssd.conf`**: `id_provider = ldap`,
   `ldap_uri = ldap://<server>`, `ldap_search_base = dc=lab,dc=local`. In this
   lab there is no TLS, so allow it explicitly
   (`ldap_id_use_start_tls = False` +
   `ldap_auth_disable_tls_never_use_in_production = True`). Mode `0600`.
2. Switch NSS/PAM to SSSD with **`authselect select sssd with-mkhomedir`**.
3. **Enable and start `sssd`** (clear its cache with `sss_cache -E` if needed).

The point: on RHEL you don't edit `nsswitch`/`pam` by hand — `authselect` wires
the SSSD plugins; SSSD then answers `getent`/`id` from the directory. `sssd.conf`
must be `0600` or SSSD refuses to start.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/

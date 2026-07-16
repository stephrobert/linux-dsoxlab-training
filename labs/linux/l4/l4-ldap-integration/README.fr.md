# Lab — authentification LDAP avec SSSD

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-ldap-integration`

## Rappel

[**SSSD + LDAP sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/)

Un 389 Directory Server (`dc=lab,dc=local`) contient un utilisateur posix `alice`.
SSSD est le démon client : `/etc/sssd/sssd.conf` (mode `0600`) avec
`id_provider = ldap` + `ldap_uri` + `ldap_search_base` lui dit où chercher.
`authselect select sssd with-mkhomedir` branche NSS/PAM sur SSSD. Ensuite
`getent passwd`/`id` répondent depuis l'annuaire. Pas de TLS dans ce lab, il faut
donc l'autoriser explicitement.

L'IP du serveur est dans `/root/ldap-server.env`.

## Objectifs

- `getent passwd alice` résout l'utilisateur de l'annuaire (uid 10001) ;
- `id alice` fonctionne ;
- le profil authselect actif est `sssd`.

## Valider

```bash
dsoxlab check l4-ldap-integration
```

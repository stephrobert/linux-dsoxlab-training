# Challenge — l4-ldap-integration

## Mission

Branche ce client sur le 389 Directory Server avec SSSD pour que les utilisateurs
de l'annuaire soient résolus.

## Objectif (état attendu)

1. `getent passwd alice` renvoie l'utilisateur de l'annuaire (uid `10001`).
2. `id alice` fonctionne.
3. Le profil authselect actif est `sssd`.

## Contraintes

- Pas de compte local : `alice` doit venir de LDAP, pas de `/etc/passwd`.
- `sssd.conf` doit être en `0600` sinon sssd ne démarre pas.
- L'IP du serveur est dans `/root/ldap-server.env`. Pas de TLS ici — autorise-le
  explicitement.
- On lit `getent`, `id` et `authselect current`.

## Validation

```bash
dsoxlab check l4-ldap-integration
```

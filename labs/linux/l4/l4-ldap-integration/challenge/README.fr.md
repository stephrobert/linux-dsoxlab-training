# Laisser les utilisateurs de l'annuaire se connecter

## La situation

Un **389 Directory Server** central (base `dc=lab,dc=local`) contient tes
comptes, dont un utilisateur posix **`alice`**. Cette machine cliente ne le
connaît pas encore : elle ne sait pas résoudre `alice`. Branche-la avec **SSSD**
pour que les utilisateurs de l'annuaire soient résolus et puissent
s'authentifier. Tu ne créeras aucun compte local.

L'idée : sur RHEL, on n'édite pas `nsswitch` ni `pam` à la main, un outil dédié
bascule le système sur les greffons SSSD ; SSSD répond ensuite aux résolutions
d'identité depuis l'annuaire. Attention, il est pointilleux sur les permissions
de sa propre configuration et refuse de démarrer si elles sont trop ouvertes.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/

## Ce qui est demandé

### Mission

Branche ce client sur le 389 Directory Server avec SSSD pour que les utilisateurs
de l'annuaire soient résolus.

### Objectif (état attendu)

1. `getent passwd alice` renvoie l'utilisateur de l'annuaire (uid `10001`).
2. `id alice` fonctionne.
3. Le profil authselect actif est `sssd`.

### Contraintes

- Pas de compte local : `alice` doit venir de LDAP, pas de `/etc/passwd`.
- `sssd.conf` doit être en `0600` sinon sssd ne démarre pas.
- L'IP du serveur est dans `/root/ldap-server.env`. Pas de TLS ici — autorise-le
  explicitement.
- On lit `getent`, `id` et `authselect current`.

### Validation

```bash
dsoxlab check l4-ldap-integration
```

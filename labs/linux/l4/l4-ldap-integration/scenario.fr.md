# Contexte — laisser les utilisateurs de l'annuaire se connecter

Un **389 Directory Server** central (base `dc=lab,dc=local`) contient tes comptes
— dont un utilisateur posix **`alice`**. Cette machine cliente ne le connaît pas
encore : `getent passwd alice` ne renvoie rien. Branche-la avec **SSSD** pour que
les utilisateurs de l'annuaire soient résolus et puissent s'authentifier. Tu ne
créeras aucun compte local.

Ta mission, sur la VM cliente (l'IP du serveur est dans `/root/ldap-server.env`) :

1. Configure **`/etc/sssd/sssd.conf`** : `id_provider = ldap`,
   `ldap_uri = ldap://<serveur>`, `ldap_search_base = dc=lab,dc=local`. En lab il
   n'y a pas de TLS, autorise-le donc explicitement
   (`ldap_id_use_start_tls = False` +
   `ldap_auth_disable_tls_never_use_in_production = True`). Mode `0600`.
2. Bascule NSS/PAM vers SSSD avec **`authselect select sssd with-mkhomedir`**.
3. **Active et démarre `sssd`** (vide son cache avec `sss_cache -E` au besoin).

L'idée : sur RHEL on n'édite pas `nsswitch`/`pam` à la main — `authselect` branche
les greffons SSSD ; SSSD répond ensuite à `getent`/`id` depuis l'annuaire.
`sssd.conf` doit être en `0600` sinon SSSD refuse de démarrer.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/

# Contexte — laisser les utilisateurs de l'annuaire se connecter

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
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/

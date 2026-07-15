# Contexte — donner du mordant à la politique de mots de passe

Des mots de passe qui n'expirent jamais et peuvent tenir en un caractère, c'est
un constat d'audit assuré. Durcis la politique à trois niveaux : le compte
existant, le défaut système pour les nouveaux comptes, et la règle de complexité.

Ta mission, sur la VM :

1. Pour l'utilisateur **`bob`**, règle l'expiration avec `chage` : **max 60**
   jours, **min 7** jours, **avertissement 7** jours avant expiration.
2. Passe le défaut système **`PASS_MAX_DAYS`** à **60** dans `/etc/login.defs`
   (s'applique aux comptes créés ensuite).
3. Exige une longueur mini de **12** dans `/etc/security/pwquality.conf`
   (`minlen`).

L'idée : `chage` règle l'expiration par compte, `login.defs` amorce les défauts
des nouveaux utilisateurs, et `pwquality` impose la complexité. `chage -l bob`
montre le résultat.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

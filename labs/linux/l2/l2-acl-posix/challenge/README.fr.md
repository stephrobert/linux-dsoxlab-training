# Un accès qu'ugo ne sait pas exprimer

## La situation

`root` possède `/srv/projet` et `report.txt`. Tu dois donner à **un utilisateur
précis** un accès en écriture au fichier et à **un groupe** un accès en lecture
au répertoire — sans changer le propriétaire ni les bits `ugo`, et sans les
rendre lisibles par tout le monde. C'est exactement le rôle des **ACL POSIX**.

L'idée : une ACL ajoute des entrées utilisateur ou groupe nommés par-dessus les
droits `ugo`, sans toucher à ces derniers. Et ce dont héritent les fichiers créés
plus tard ne se règle pas au même endroit que l'accès accordé aujourd'hui.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/

## Ce qui est demandé

### Mission

Accorde des accès fins par ACL sur `/srv/projet` sans toucher au propriétaire ni
aux droits ugo.

### Objectif (état attendu)

1. `carol` a `rw` (ACL utilisateur) sur `/srv/projet/report.txt`.
2. `auditors` a `r-x` (ACL groupe) sur `/srv/projet`.
3. Une ACL **par défaut** donne `r` à `auditors` sur les futurs fichiers de `/srv/projet`.

### Contraintes

- `setfacl -m` pour ajouter, `d:` pour l'ACL par défaut. Vérifie avec `getfacl`.
- La validation lit les **ACL réelles** (`getfacl`), pas la commande tapée.

### Validation

```bash
dsoxlab check l2-acl-posix
```

# Un montage de données bloqué en lecture seule

## La situation

Les applications qui écrivent dans `/srv/data` échouent : le filesystem est monté
en **lecture seule**, et pire, une faute de frappe s'est glissée dans
`/etc/fstab` — à un vrai reboot, la machine tomberait en mode urgence.
Diagnostique et répare.

L'idée : une option de montage invalide dans `/etc/fstab` ne se voit pas tant que
personne ne relit le fichier ; au démarrage, elle bloque tout. Il faut donc les
deux : rendre `/srv/data` de nouveau inscriptible, et s'assurer que la
déclaration est saine avant de tenter un redémarrage.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/

## Ce qui est demandé

### Mission

`/srv/data` est en lecture seule et `/etc/fstab` est cassé. Répare.

### Objectif (état attendu)

1. `/srv/data` est monté en **lecture-écriture** (et inscriptible).
2. `mount -a` réussit (retour 0).
3. L'option invalide (`defalts`) a disparu de `/etc/fstab`.

### Contraintes

- Corrige l'entrée fstab, puis `mount -o remount,rw /srv/data`. Teste avec
  `mount -a`. La validation lit l'**état réel** (options du montage, écriture,
  mount -a).

### Validation

```bash
dsoxlab check l3-fs-readonly-recover
```

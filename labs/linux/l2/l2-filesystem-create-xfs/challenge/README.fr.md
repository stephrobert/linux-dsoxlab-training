# Poser un vrai filesystem sur une partition

## La situation

Une partition vierge attend. Une partition n'est qu'un espace réservé tant
qu'elle ne porte pas de **filesystem**. Ta mission : la formater en **XFS** (le
défaut RHEL, excellent pour les gros fichiers et la montée en charge), lui donner
un **label** pour l'identifier facilement, et la monter.

L'idée : un label est une étiquette portée par le filesystem lui-même. Il permet
de désigner ce dernier par un nom stable, plutôt que par un nom de périphérique
fragile qui peut changer d'un démarrage à l'autre.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/

## Ce qui est demandé

### Mission

Une partition vierge est prête sur la VM (voir `lsblk`). Formate-la et monte-la.

### Objectif (état attendu)

1. La partition porte un filesystem **XFS**.
2. Son **label** est `DATA`.
3. Elle est **montée** sur `/srv/xfs`.
4. Le montage est de type **xfs**.

### Contraintes

- `mkfs.xfs -L DATA <partition>` pour le format + label, `mount` pour le montage.
  Repère la partition avec `lsblk` (celle sans filesystem).
- La validation lit l'**état réel** (type, label, montage), pas la commande.

### Validation

```bash
dsoxlab check l2-filesystem-create-xfs
```

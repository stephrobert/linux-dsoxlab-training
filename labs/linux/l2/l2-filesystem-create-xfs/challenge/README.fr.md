# Challenge — l2-filesystem-create-xfs

## Mission

Une partition vierge est prête sur la VM (voir `lsblk`). Formate-la et monte-la.

## Objectif (état attendu)

1. La partition porte un filesystem **XFS**.
2. Son **label** est `DATA`.
3. Elle est **montée** sur `/srv/xfs`.
4. Le montage est de type **xfs**.

## Contraintes

- `mkfs.xfs -L DATA <partition>` pour le format + label, `mount` pour le montage.
  Repère la partition avec `lsblk` (celle sans filesystem).
- La validation lit l'**état réel** (type, label, montage), pas la commande.

## Validation

```bash
dsoxlab check l2-filesystem-create-xfs
```

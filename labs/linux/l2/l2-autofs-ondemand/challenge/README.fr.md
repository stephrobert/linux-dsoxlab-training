# Challenge — l2-autofs-ondemand

## Mission

Configure autofs pour monter le disque supplémentaire à la demande sous
`/autofs/data`.

## Objectif (état attendu)

1. Le service **autofs** tourne.
2. Une carte **maître** associe `/autofs` à `/etc/auto.lab`.
3. La carte **de montage** `/etc/auto.lab` décrit `data` en `xfs` vers la partition.
4. Accéder à `/autofs/data` **déclenche** le montage (`marker.txt` lisible, type xfs).

## Contraintes

- Partition cible dans `/root/autofs-disk.env`. `systemctl restart autofs` après
  édition des cartes. La validation **déclenche l'accès** et lit l'état réel.

## Validation

```bash
dsoxlab check l2-autofs-ondemand
```

# Monter seulement quand c'est nécessaire

## La situation

Certains filesystems ne doivent pas rester montés en permanence : un disque
rarement utilisé, un partage réseau. **autofs** les monte **à l'accès** et les
démonte après un délai d'inactivité, économisant les ressources et évitant les
montages fantômes. Ici, le disque supplémentaire porte un XFS ; câble-le pour
qu'un accès à `/autofs/data` le monte.

L'idée : autofs ne monte rien tant que le chemin n'est pas sollicité, et il
démonte de lui-même quand plus personne ne s'en sert. Encore faut-il lui décrire
ce qu'il doit monter, et sous quel chemin.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/

## Ce qui est demandé

### Mission

Configure autofs pour monter le disque supplémentaire à la demande sous
`/autofs/data`.

### Objectif (état attendu)

1. Le service **autofs** tourne.
2. Une carte **maître** associe `/autofs` à `/etc/auto.lab`.
3. La carte **de montage** `/etc/auto.lab` décrit `data` en `xfs` vers la partition.
4. Accéder à `/autofs/data` **déclenche** le montage (`marker.txt` lisible, type xfs).

### Contraintes

- Partition cible dans `/root/autofs-disk.env`. `systemctl restart autofs` après
  édition des cartes. La validation **déclenche l'accès** et lit l'état réel.

### Validation

```bash
dsoxlab check l2-autofs-ondemand
```

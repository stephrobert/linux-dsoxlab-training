# Un paramètre noyau qui tient

## La situation

Tu veux que le noyau redémarre automatiquement dix secondes après un panic
(`panic=10`) — et ça doit tenir aux reboots **et** aux mises à jour du noyau.
Éditer le `/proc/cmdline` vivant est impossible ; le paramètre a sa place dans le
**bootloader**.

L'idée : un paramètre noyau doit atteindre deux populations distinctes, les
noyaux déjà installés et ceux qui le seront demain. Rien ne garantit qu'un même
geste couvre les deux, et sur une distribution à entrées de démarrage BLS c'est
précisément là que le piège se referme.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/durcissement/grub/

## Ce qui est demandé

### Mission

Ajoute le paramètre noyau `panic=10` de façon persistante.

### Objectif (état attendu)

1. Les arguments du noyau par défaut incluent `panic=10`
   (`grubby --info=DEFAULT`).
2. `/etc/default/grub` contient `panic=10` (pour les futurs noyaux).

### Contraintes

- Les noyaux courants (`grubby`) ET le modèle (`/etc/default/grub`) doivent
  l'avoir — sinon c'est perdu à la prochaine mise à jour du noyau.
- On lit `grubby --info=DEFAULT` et `/etc/default/grub`.

### Validation

```bash
dsoxlab check l3-grub-kernel-args
```

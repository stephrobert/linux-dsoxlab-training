# Challenge — l3-grub-kernel-args

## Mission

Ajoute le paramètre noyau `panic=10` de façon persistante.

## Objectif (état attendu)

1. Les arguments du noyau par défaut incluent `panic=10`
   (`grubby --info=DEFAULT`).
2. `/etc/default/grub` contient `panic=10` (pour les futurs noyaux).

## Contraintes

- Les noyaux courants (`grubby`) ET le modèle (`/etc/default/grub`) doivent
  l'avoir — sinon c'est perdu à la prochaine mise à jour du noyau.
- On lit `grubby --info=DEFAULT` et `/etc/default/grub`.

## Validation

```bash
dsoxlab check l3-grub-kernel-args
```

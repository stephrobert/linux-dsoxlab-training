# Régler la machine pour le débit

## La situation

Cette machine fait du batch intensif en données mais reste sur le profil tuned
**`balanced`** par défaut. Bascule-la sur un profil taillé pour le **débit**,
pour que les réglages noyau (gouverneur CPU, I/O, VM) soient prévus pour une
charge soutenue, et que ça survive à un reboot.

L'idée : `tuned` regroupe des dizaines de réglages noyau et sysfs dans des
profils nommés, un par grand type de charge. Le profil retenu est enregistré sur
disque, et c'est ce qui le fait tenir aux reboots. Reste à savoir lequel choisir
et comment en changer.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/

## Ce qui est demandé

### Mission

Bascule le profil tuned actif sur `throughput-performance`, durablement.

### Objectif (état attendu)

1. Le service `tuned` tourne.
2. `tuned-adm active` → **`throughput-performance`**.
3. `/etc/tuned/active_profile` contient `throughput-performance` (persistance).

### Contraintes

- `tuned-adm profile throughput-performance`. La validation lit le **profil
  réellement actif**, pas la commande.

### Validation

```bash
dsoxlab check l3-tuned-profile
```

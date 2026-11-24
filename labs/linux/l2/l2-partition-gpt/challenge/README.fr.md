# Découper un disque en GPT

## La situation

La machine a un disque supplémentaire, vierge : c'est celui-là, et lui seul, que
tu dois découper. Avant de porter un filesystem, un membre LVM ou un périphérique
RAID, il lui faut une **table de partition**. Les systèmes modernes utilisent
**GPT** (sans les limites du vieux MBR : 4 partitions et 2 Tio). Ta mission :
poser GPT et découper deux partitions.

L'idée : écrire une table de partition ne suffit pas à la rendre visible. Le
noyau garde sa vue de l'ancienne tant qu'on ne lui demande pas de la relire, ou
tant que la machine n'a pas redémarré.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/

## Ce qui est demandé

### Mission

Le disque supplémentaire de la VM est **vierge**. Pose une table GPT et deux
partitions.

### Objectif (état attendu)

1. Le disque a une table de partition **GPT**.
2. **Deux** partitions.
3. Partition 1 = **512 Mio**.
4. Partition 2 = **1 Gio**.
5. La table est relue par le noyau (`partprobe`) — les partitions apparaissent
   dans `lsblk`.

### Contraintes

- `parted` (ou `fdisk`) pour la table et les partitions ; `partprobe` pour
  informer le noyau. Repère le disque avec `lsblk` (le disque sans partition).
- La validation lit l'**état réel** (PTTYPE, partitions, tailles), pas la commande.

### Validation

```bash
dsoxlab check l2-partition-gpt
```

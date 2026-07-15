# Challenge — l2-partition-gpt

## Mission

Le disque supplémentaire de la VM est **vierge**. Pose une table GPT et deux
partitions.

## Objectif (état attendu)

1. Le disque a une table de partition **GPT**.
2. **Deux** partitions.
3. Partition 1 = **512 Mio**.
4. Partition 2 = **1 Gio**.
5. La table est relue par le noyau (`partprobe`) — les partitions apparaissent
   dans `lsblk`.

## Contraintes

- `parted` (ou `gdisk`) pour la table et les partitions ; `partprobe` pour
  informer le noyau. Repère le disque avec `lsblk` (le disque sans partition).
- La validation lit l'**état réel** (PTTYPE, partitions, tailles), pas la commande.

## Validation

```bash
dsoxlab check l2-partition-gpt
```

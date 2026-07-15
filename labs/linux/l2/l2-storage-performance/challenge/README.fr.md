# Challenge — l2-storage-performance

## Mission

`/srv/data` est monté avec les options par défaut (atime activé). Optimise-le
pour une charge très lue avec `noatime`, durablement.

## Objectif (état attendu)

1. `/srv/data` est **monté**.
2. Le montage réel inclut l'option **`noatime`** (`findmnt /srv/data`).
3. `/etc/fstab` déclare **`noatime`** pour `/srv/data` (persistance reboot).

## Contraintes

- Édite les options fstab (4ᵉ champ), puis `mount -o remount /srv/data` pour
  activer sans reboot. Ne démonte pas / ne reformate pas.
- La validation lit l'**état réel** (options du montage + contenu fstab).

## Validation

```bash
dsoxlab check l2-storage-performance
```

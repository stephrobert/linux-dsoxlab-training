# Arrêter de gaspiller des I/O sur les dates d'accès

## La situation

`/srv/data` sert une charge très sollicitée en lecture. Par défaut, Linux met à
jour la **date d'accès** (atime) de chaque fichier à la lecture, ce qui
transforme les lectures en écritures et dégrade les performances. Le correctif
standard est l'option de montage **`noatime`**. Ta mission : l'appliquer —
maintenant et durablement.

L'idée : les options de montage règlent le comportement d'un filesystem ;
`noatime` supprime les mises à jour d'atime. Reste à savoir comment le rendre
actif tout de suite **et** persistant au redémarrage : ce sont deux gestes
distincts.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/

## Ce qui est demandé

### Mission

`/srv/data` est monté avec les options par défaut (atime activé). Optimise-le
pour une charge très lue avec `noatime`, durablement.

### Objectif (état attendu)

1. `/srv/data` est **monté**.
2. Le montage réel inclut l'option **`noatime`** (`findmnt /srv/data`).
3. `/etc/fstab` déclare **`noatime`** pour `/srv/data` (persistance reboot).

### Contraintes

- Édite les options fstab (4ᵉ champ), puis `mount -o remount /srv/data` pour
  activer sans reboot. Ne démonte pas / ne reformate pas.
- La validation lit l'**état réel** (options du montage + contenu fstab).

### Validation

```bash
dsoxlab check l2-storage-performance
```

# /data manque d'espace

## La situation

Sur **alma-rhcsa-1.lab**, une application écrit dans `/data`, un volume XFS de
1 GiB porté par le volume logique `vgdata/lvdata`. Le groupe de volumes dispose
encore d'espace libre sur son volume physique. Tu dois agrandir `/data` **sans
interruption** et t'assurer que ça tient après un reboot.

Le piège : le volume logique et le filesystem posé dessus sont deux couches
distinctes. Agrandir l'une ne suffit pas, et tant que l'autre n'a pas suivi,
l'espace ajouté reste invisible pour l'application.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/

## Ce qui est demandé

### Mission

`/data` (XFS, 1 GiB, porté par `vgdata/lvdata`) est trop petit. Agrandis-le, en
ligne, et garde-le persistant.

### Objectif (état à atteindre)

- `vgdata/lvdata` fait **≥ 3 GiB**.
- Le filesystem XFS de `/data` **reflète** l'extension (`df` montre ≥ 3 G).
- `/data` est monté et déclaré dans `/etc/fstab` **par UUID** (survit au reboot).

### Contraintes

- Sans démonter `/data` (extension en ligne).
- La validation vérifie l'**état du système**, pas les commandes tapées :
  étendre le LV sans agrandir le XFS échoue.

### Validation

```bash
dsoxlab check l2-lvm-extend-persist
```

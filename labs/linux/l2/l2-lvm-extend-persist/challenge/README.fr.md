# Challenge — l2-lvm-extend-persist

## Mission

`/data` (XFS, 1 GiB, porté par `vgdata/lvdata`) est trop petit. Agrandis-le, en
ligne, et garde-le persistant.

## Objectif (état à atteindre)

- `vgdata/lvdata` fait **≥ 3 GiB**.
- Le filesystem XFS de `/data` **reflète** l'extension (`df` montre ≥ 3 G).
- `/data` est monté et déclaré dans `/etc/fstab` **par UUID** (survit au reboot).

## Contraintes

- Sans démonter `/data` (extension en ligne).
- La validation vérifie l'**état du système**, pas les commandes tapées :
  étendre le LV sans agrandir le XFS échoue.

## Validation

```bash
dsoxlab check l2-lvm-extend-persist
```

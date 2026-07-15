# Challenge — l3-fs-readonly-recover

## Mission

`/srv/data` est en lecture seule et `/etc/fstab` est cassé. Répare.

## Objectif (état attendu)

1. `/srv/data` est monté en **lecture-écriture** (et inscriptible).
2. `mount -a` réussit (retour 0).
3. L'option invalide (`defalts`) a disparu de `/etc/fstab`.

## Contraintes

- Corrige l'entrée fstab, puis `mount -o remount,rw /srv/data`. Teste avec
  `mount -a`. La validation lit l'**état réel** (options du montage, écriture,
  mount -a).

## Validation

```bash
dsoxlab check l3-fs-readonly-recover
```

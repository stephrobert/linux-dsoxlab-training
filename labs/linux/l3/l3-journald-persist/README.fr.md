# Lab — journald persistant

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-journald-persist`

## Rappel

[**Journaux systemd sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/)

journald garde les logs dans `/run/log/journal` (volatile) par défaut. Avec
`Storage=persistent` (dans `journald.conf` ou un drop-in `journald.conf.d/`)
**et** un répertoire `/var/log/journal`, les logs vont sur disque et survivent
aux reboots. Redémarre `systemd-journald` et `journalctl --flush` pour les
basculer. `journalctl -b -1` lit le boot précédent.

## Objectifs

- `Storage=persistent` dans la config journald ;
- `/var/log/journal` existe ;
- un vrai fichier `.journal` y est écrit.

## Valider

```bash
dsoxlab check l3-journald-persist
```

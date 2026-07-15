# Challenge — l3-journald-persist

## Mission

Le journal systemd est volatile (perdu au reboot). Rends-le persistant.

## Objectif (état attendu)

1. `/var/log/journal` existe (répertoire).
2. La config journald déclare **`Storage=persistent`**.
3. Un fichier `.journal` est écrit sous `/var/log/journal` (journald a basculé).

## Contraintes

- `Storage=persistent` (journald.conf ou drop-in), `mkdir /var/log/journal`,
  puis `systemctl restart systemd-journald` + `journalctl --flush`. La
  validation lit l'**état réel** (config, répertoire, fichier journal).

## Validation

```bash
dsoxlab check l3-journald-persist
```

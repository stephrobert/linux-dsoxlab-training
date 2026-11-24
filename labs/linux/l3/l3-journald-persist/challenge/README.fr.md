# Garder les logs après un reboot

## La situation

Sur cette machine, le journal est **volatile** : tout ce que montre `journalctl`
est perdu au reboot, un cauchemar quand il faut enquêter sur la panne d'un
serveur. Rends le journal systemd **persistant**.

L'idée : par défaut, journald écrit dans un emplacement volatile, vidé à chaque
démarrage. Basculer vers un stockage qui survit au reboot ne tient pas à un seul
réglage : il faut que la configuration l'autorise, et que la destination soit
prête à recevoir le journal.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/

## Ce qui est demandé

### Mission

Le journal systemd est volatile (perdu au reboot). Rends-le persistant.

### Objectif (état attendu)

1. `/var/log/journal` existe (répertoire).
2. La config journald déclare **`Storage=persistent`**.
3. Un fichier `.journal` est écrit sous `/var/log/journal` (journald a basculé).

### Contraintes

- `Storage=persistent` (journald.conf ou drop-in), `mkdir /var/log/journal`,
  puis `systemctl restart systemd-journald` + `journalctl --flush`. La
  validation lit l'**état réel** (config, répertoire, fichier journal).

### Validation

```bash
dsoxlab check l3-journald-persist
```

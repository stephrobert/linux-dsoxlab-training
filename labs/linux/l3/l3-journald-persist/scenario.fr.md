# Contexte — garder les logs après un reboot

Sur cette machine, le journal est **volatile** : tout ce que montre `journalctl`
est perdu au reboot, un cauchemar quand il faut enquêter sur la panne d'un
serveur. Rends le journal systemd **persistant**.

Ta mission, sur la VM :

1. Règle **`Storage=persistent`** pour journald (dans
   `/etc/systemd/journald.conf` ou, plus propre, un drop-in sous
   `/etc/systemd/journald.conf.d/`).
2. Crée le répertoire **`/var/log/journal`**.
3. **Redémarre** `systemd-journald` (et `journalctl --flush`) pour qu'il commence
   à écrire sur disque.

L'idée : journald garde les logs dans `/run` (volatile) sauf si `/var/log/journal`
existe et que `Storage` l'autorise ; `persistent` force le stockage sur disque
qui survit aux reboots. `journalctl --disk-usage` et `journalctl -b -1` (boot
précédent) le confirment.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/

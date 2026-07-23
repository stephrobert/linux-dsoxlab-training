# Contexte — garder les logs après un reboot

Sur cette machine, le journal est **volatile** : tout ce que montre `journalctl`
est perdu au reboot, un cauchemar quand il faut enquêter sur la panne d'un
serveur. Rends le journal systemd **persistant**.

L'idée : par défaut, journald écrit dans un emplacement volatile, vidé à chaque
démarrage. Basculer vers un stockage qui survit au reboot ne tient pas à un seul
réglage : il faut que la configuration l'autorise, et que la destination soit
prête à recevoir le journal.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/

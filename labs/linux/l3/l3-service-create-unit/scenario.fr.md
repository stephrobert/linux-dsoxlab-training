# Contexte — transformer un programme en service géré

Un petit programme (`/usr/local/bin/labapp.sh`) doit tourner comme un vrai
**service systemd** : démarré maintenant, redémarré en cas d'échec, et relancé
automatiquement au boot. Là, il n'a aucune unit.

Ta mission, sur la VM :

1. Écris une unit `/etc/systemd/system/labapp.service` (`Type=simple`,
   `ExecStart=/usr/local/bin/labapp.sh`, un `Restart=` raisonnable, et une
   section `[Install]`).
2. Recharge systemd (`systemctl daemon-reload`).
3. **Démarre et active** le service (`systemctl enable --now labapp`).

L'idée : un fichier unit décrit *comment* lancer quelque chose ; `daemon-reload`
fait relire une unit nouvelle/modifiée à systemd ; `start` la lance maintenant,
`enable` la relie à une cible pour qu'elle démarre au boot. `systemctl status
labapp` montre le résultat.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/

# Contexte — relever le plafond de ressources d'une application

Le service qui tourne sous **`appuser`** ouvre des milliers de fichiers et bute
sur la limite par défaut de fichiers ouverts. Tu dois relever sa limite `nofile`
— et la rendre durable pour chaque nouvelle session, pas juste ce shell.

Ta mission, sur la VM — pour l'utilisateur `appuser` :

1. Règle la limite **souple** de fichiers ouverts (`nofile`) à **4096**.
2. Règle la limite **dure** à **8192**.
3. Fais-le dans `/etc/security/limits.d/` pour que ça s'applique à chaque login
   (via `pam_limits`).

L'idée : `ulimit` montre/règle les limites du shell courant, mais la politique
durable vit dans `/etc/security/limits.conf` et `/etc/security/limits.d/*.conf`
(`<qui> <soft|hard> <item> <valeur>`). La limite souple est le défaut, la limite
dure est le plafond que l'utilisateur peut atteindre. Vérifie avec
`su - appuser -c 'ulimit -Sn'`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/

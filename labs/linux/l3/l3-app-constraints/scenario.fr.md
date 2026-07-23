# Contexte — relever le plafond de ressources d'une application

Le service qui tourne sous **`appuser`** ouvre des milliers de fichiers et bute
sur la limite par défaut de fichiers ouverts. Tu dois relever sa limite `nofile`
— et la rendre durable pour chaque nouvelle session, pas juste ce shell.

L'idée : ce qu'on ajuste dans un shell ne vaut que pour ce shell. Une politique
durable se déclare ailleurs et s'applique à l'ouverture de chaque session. Et
deux valeurs cohabitent : la limite souple, qui est le défaut appliqué, et la
limite dure, qui est le plafond que l'utilisateur peut atteindre.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/

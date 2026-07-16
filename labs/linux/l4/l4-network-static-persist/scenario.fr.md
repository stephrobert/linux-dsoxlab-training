# Contexte — une adresse statique qui survit au reboot

Un service a besoin d'une IPv4 fixe sur cette machine, sur une interface dédiée —
et elle doit revenir après un reboot, pas disparaître. Un `ip addr add` ne dure
que jusqu'au prochain reboot ; la façon durable sur RHEL est un **profil de
connexion NetworkManager**.

Ta mission, sur la VM (travaille sur l'interface dédiée `lab0`, **ne touche
jamais à l'interface de gestion** — c'est ton lien de gestion) :

1. Crée une connexion NetworkManager nommée **`lab-static`** sur l'interface
   `lab0` (type `dummy`).
2. Donne-lui l'adresse statique **`192.0.2.50/24`** (`ipv4.method manual`).
3. **Active-la** (`nmcli con up lab-static`).

L'idée : `nmcli con add … ipv4.method manual ipv4.addresses …` écrit un profil
sous `/etc/NetworkManager/system-connections/`, et c'est ça qui fait survivre
l'adresse au reboot. `ip addr add`, non.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/

# Contexte — une adresse statique qui survit au reboot

Un service a besoin d'une IPv4 fixe sur cette machine, sur une interface dédiée,
et elle doit revenir après un reboot, pas disparaître. Un `ip addr add` ne dure
que jusqu'au prochain redémarrage ; la façon durable sur RHEL est un **profil de
connexion NetworkManager**.

Tu travailles sur l'interface dédiée `lab0`. **Ne touche jamais à l'interface de
gestion**, celle qui porte ta route par défaut : c'est ton lien vers la machine.

L'idée : un profil de connexion NetworkManager est écrit sur disque, et c'est ce
fichier qui fait revenir l'adresse après un reboot. Encore faut-il que le profil
soit non seulement créé, mais aussi actif : les deux se vérifient séparément.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/

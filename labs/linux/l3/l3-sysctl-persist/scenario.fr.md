# Contexte — durcir le noyau, définitivement

Un scan de sécurité épingle cet hôte : il route des paquets IP et accepte les
redirections ICMP — aucun des deux n'est souhaité sur un serveur normal.
Désactive-les, au niveau du noyau, pour que ça tienne maintenant **et** après un
reboot.

Ta mission, sur la VM :

1. Règle `net.ipv4.ip_forward = 0`.
2. Règle `net.ipv4.conf.all.accept_redirects = 0`.
3. Rends-le **persistant** dans `/etc/sysctl.d/` et applique à chaud
   (`sysctl --system`).

L'idée : `sysctl -w` change une valeur maintenant mais la perd au reboot ; un
fichier dans `/etc/sysctl.d/*.conf` la rend durable, et `sysctl --system` les
relit tous. `sysctl -n <param>` lit la valeur active.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/

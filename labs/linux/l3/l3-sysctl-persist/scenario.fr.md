# Contexte — durcir le noyau, définitivement

Un scan de sécurité épingle cet hôte : il route des paquets IP et accepte les
redirections ICMP, alors qu'aucun des deux n'est souhaité sur un serveur normal.
Désactive-les, au niveau du noyau, pour que ça tienne maintenant **et** après un
reboot.

L'idée : un paramètre `sysctl` se change à chaud, mais ce qui est posé à chaud
disparaît au redémarrage. Rendre le réglage actif tout de suite et le rendre
durable sont deux gestes distincts : les tests regarderont les deux.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/

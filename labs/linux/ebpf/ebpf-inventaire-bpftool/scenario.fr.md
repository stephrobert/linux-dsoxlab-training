# Contexte : le programme que personne n'a déployé

Lors d'une revue de sécurité, l'équipe réalise qu'elle ne sait pas ce que le
noyau de ce serveur exécute. Les sondes eBPF y sont courantes, systemd en charge
lui-même pour filtrer le réseau et les périphériques de ses services. Mais un
programme eBPF s'exécute dans le noyau avec des droits étendus, et ce qui s'y
loge sans que personne l'ait décidé est exactement ce qu'un attaquant installé
sur la machine ferait pour y rester discret.

Un collègue a remarqué un service au nom banal, du genre « collecte de
télémétrie », que personne ne se souvient d'avoir déployé. La demande est simple
et précise : dire ce qui est chargé, retrouver ce qui le porte, et si cela n'a
rien à faire là, l'arrêter pour de bon, c'est-à-dire que le service ne doit pas
revenir au prochain démarrage. Sans toucher à ce que le système charge lui-même :
un inventaire qui casse la machine ne vaut pas mieux que le programme qu'il
cherche.

Ce qui sera vérifié, c'est l'état de la machine : ce que le noyau porte encore,
si le service peut revenir, et si ta réponse nomme bien le service et le type du
programme. Pas les commandes que tu auras tapées.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/surface-attaque-bpf/

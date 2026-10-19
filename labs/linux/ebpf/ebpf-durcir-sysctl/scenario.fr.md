# Contexte : l'audit qui trouve eBPF grand ouvert

La semaine dernière, un prestataire a profilé une application sur ce serveur.
Son outil lançait des sondes eBPF sans être root, et pour que cela fonctionne
quelqu'un a relâché les réglages du noyau, à la main, puis a oublié d'y revenir.
Le ticket est clos, le prestataire est parti, et l'audit de sécurité du
trimestre vient de tomber : n'importe quel compte ordinaire de la machine peut
charger du code dans le noyau, et le compilateur qui traduit ces programmes en
instructions processeur n'est pas durci.

Ce n'est pas un détail. Plusieurs failles du noyau n'ont été exploitables que par
un appelant sans privilège, et fermer cette porte est l'un des gestes les moins
coûteux du durcissement Linux. Mais un réglage noyau corrigé à chaud n'est
corrigé que jusqu'au prochain redémarrage, et celui qui a ouvert la porte a
peut-être aussi laissé de quoi la rouvrir.

Ce qui sera vérifié, c'est l'état de la machine : ce que le noyau applique
maintenant, ce qu'il refuse réellement à un utilisateur sans privilège, et ce
qu'il appliquera après un rechargement de la configuration. Pas les commandes
que tu auras tapées.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/durcir-ebpf/

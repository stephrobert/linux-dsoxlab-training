# Contexte : le processus que personne ne reconnaît

Un serveur de la maison écrit régulièrement dans un fichier que personne ne sait
situer. Le service qui s'en occupe s'appelle `lab-mystere`, mais le programme
qui tourne derrière porte un nom que ni la documentation ni l'équipe ne
reconnaissent, et le fichier qu'il alimente est caché quelque part sur le
disque. Les outils habituels ne le montrent pas : le fichier n'est ouvert que
l'espace d'un instant, puis refermé aussitôt.

Le noyau, lui, a tout vu. Avec eBPF, on lui demande de raconter ce qui se passe :
quels programmes sont lancés, quels fichiers sont ouverts, et par qui. L'enjeu
est de retrouver l'identité du processus et la cible de ses écritures **sans
l'arrêter ni le modifier** : c'est un service en production, on observe, on ne
touche pas.

Ce qui sera vérifié, c'est l'état de la machine : des outils de traçage qui
fonctionnent vraiment, une réponse qui correspond à la réalité de la machine, et
un service resté intact. Pas les commandes que tu auras tapées.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/tracer/bpftrace/

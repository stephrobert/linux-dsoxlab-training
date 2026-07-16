# Contexte — l'adresse qui disparaît

`ip addr add` marche. L'adresse est là, `ping` répond, on passe à la suite — et
elle a disparu au rechargement suivant. Elle n'a jamais existé ailleurs que dans
la mémoire du noyau.

Configurer le réseau, c'est le **déclarer** : à NetworkManager sur RHEL, à
netplan sur Debian. Même objectif, deux outils — donc ce drill existe une seule
fois, et son sujet n'en nomme aucun.

**Chrono** : 4 tâches, 20 minutes, aucun indice. Tout est vérifié **après un
rechargement du réseau** : ce que tu as tapé à la main n'y survit pas.

Une règle avant toutes : tout se passe sur l'interface dédiée `lab0`. **Ne
touche jamais à l'interface de gestion** — celle qui porte ta route par défaut.
Son nom change selon le provider et la distribution, et c'est précisément
pourquoi on l'identifie par ce qu'elle fait, pas par son nom. Coupe-la et tu
perds la machine.

Lis le sujet : `dsoxlab challenge drill-network`.

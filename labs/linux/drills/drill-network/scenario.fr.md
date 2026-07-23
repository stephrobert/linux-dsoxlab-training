# Contexte — l'adresse qui disparaît

Une adresse posée à la main fonctionne tout de suite : elle est là, `ping`
répond, on passe à la suite. Et elle a disparu au rechargement suivant. Elle
n'avait jamais existé ailleurs que dans la mémoire du noyau.

Configurer le réseau, c'est le **déclarer** à l'outil qui en a la charge, et cet
outil n'est pas le même sur RHEL et sur Debian. Même objectif, deux
implémentations : ce drill existe donc une seule fois, et son sujet n'en nomme
aucune.

**Chrono** : 4 tâches, 20 minutes, aucun indice.

Tout se passe sur l'interface dédiée `lab0`. **Ne touche jamais à l'interface de
gestion**, celle qui porte ta route par défaut : son nom change selon le
provider et la distribution, et coupe-la, tu perds la machine.

Lis le sujet : `dsoxlab challenge drill-network`.

# Contexte — une panne qui ne dit pas son nom

Ce capstone n'est pas un lab de dépannage de plus. La section en compte déjà
plusieurs, et ils ont tous le même défaut : leur titre donne la moitié du
diagnostic. « Réparer un problème SELinux » vous a déjà dit où chercher.

Ici, vous ne recevez qu'un **symptôme** :

> Le site interne ne répond plus.

Le setup a monté un site qui **fonctionnait**, l'a prouvé, puis a cassé **une
seule chose**, tirée au sort parmi six. Personne ne vous dira laquelle. C'est
la différence entre appliquer une procédure et savoir dépanner.

## Les six pannes possibles

Elles ne sont listées ici que pour que vous sachiez que la liste est **finie**,
et qu'aucune n'est exotique. Toutes produisent le même symptôme vu du client.

| Famille | Ce qu'il faut savoir regarder |
|---|---|
| Service | l'état et la persistance de l'unité |
| Port | ce qui écoute, et sur quelle adresse |
| Pare-feu | ce qui est ouvert, et de façon permanente ou non |
| SELinux | le contexte du contenu servi |
| Permissions | la traversée du répertoire et la lecture du fichier |
| Écoute locale | l'adresse d'écoute, pas seulement le numéro de port |

Une septième panne a été écartée après mesure : remplir le disque **n'arrête
pas** un site statique. Servir un fichier ne demande aucune écriture.

## La règle qui fait la valeur de l'épreuve

Trois réparations « marchent » et sont notées **zéro** :

- passer SELinux en permissive ;
- arrêter le pare-feu ;
- ouvrir le docroot en écriture à tout le monde.

Chacune fait répondre le site, et chacune désarme une protection de la machine
entière pour un problème local. Un serveur qui répond parce qu'il n'est plus
protégé n'est pas réparé.

## Persistance

Ce qui ne survivrait pas à un redémarrage vaut zéro. Attention au cas SELinux :
un `chcon` survit à un reboot, mais **pas à un réétiquetage**. Les tests lancent
`restorecon` avant de conclure.

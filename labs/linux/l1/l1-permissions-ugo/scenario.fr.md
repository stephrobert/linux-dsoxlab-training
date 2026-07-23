# Contexte — donner à chaque fichier les bonnes permissions

Tout dans ton répertoire de travail est lisible par tout le monde (`0644`), ce
qui est faux pour la moitié. Un secret doit rester privé, un script doit être
exécutable, une note d'équipe doit être lisible par le groupe seulement, et il
te faut un répertoire privé. Corrige les bits de permission : ni plus, ni moins
que nécessaire.

L'idée : un mode se pose de deux manières, l'une chiffrée, l'autre symbolique,
et il se lit toujours comme trois triplets, propriétaire, groupe et autres. Le
moindre privilège, c'est accorder exactement ce qui est nécessaire, et rien de
plus.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/

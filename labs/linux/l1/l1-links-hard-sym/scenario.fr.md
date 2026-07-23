# Contexte — deux façons de pointer un fichier

Tu as `original.txt`. Un **lien physique** est un second nom pour exactement le
même fichier (même inode, mêmes données) : supprime l'original et les données
survivent. Un **lien symbolique** est un petit pointeur qui stocke un chemin ;
si la cible bouge, il pend dans le vide. Apprends à faire les deux, et un lien
symbolique vers un répertoire aussi.

L'idée : les deux se créent avec le même outil, et une fois posés, rien ne les
distingue dans un listing ordinaire. Il te faudra donc aussi savoir quoi
demander au système pour prouver lequel est lequel.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/

# Contexte — deux façons de pointer un fichier

Tu as `original.txt`. Un **lien physique** est un second nom pour exactement le
même fichier (même inode, mêmes données) ; supprime l'original et les données
survivent. Un **lien symbolique** est un petit pointeur qui stocke un chemin ; si
la cible bouge, il pend dans le vide. Apprends à faire les deux, et un lien
symbolique vers un répertoire aussi.

Ta mission — dans le répertoire de travail :

1. `copie-dure.txt` — un **lien physique** vers `original.txt` (même inode).
2. `raccourci.txt` — un **lien symbolique** vers `original.txt`.
3. `data/` — un répertoire, et `lien-data` — un **lien symbolique** vers lui.

L'idée : `ln cible nom` crée un lien physique, `ln -s cible nom` un lien
symbolique. `ls -li` montre l'inode et le compteur de liens qui prouvent lequel
est lequel.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/

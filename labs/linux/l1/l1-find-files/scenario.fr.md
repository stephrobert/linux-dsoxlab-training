# Contexte — trouver ce qu'il faut dans une arborescence de projet

Tu as reçu `projet.tar.gz`, un petit répertoire de projet. Sans ouvrir les
fichiers un par un, utilise **`find`** pour localiser exactement ce qui compte :
les logs, les gros fichiers, et ceux aux permissions privées. `find` parcourt
toute une arborescence et filtre sur le nom, la taille, le type, les permissions,
et plus encore.

Ta mission — dans le répertoire de travail :

1. **Extrais** l'archive en préservant les permissions : `tar xpzf projet.tar.gz`.
2. Produis `logs.txt` — les chemins de tous les fichiers **`*.log`** sous
   `projet/` (`find projet -name '*.log'`).
3. Produis `gros.txt` — les **fichiers réguliers de plus de 1000 octets**
   (`find projet -type f -size +1000c`).
4. Produis `prives.txt` — les **fichiers réguliers dont les permissions valent
   exactement `600`** (`find projet -type f -perm 600`).

L'idée : `-name` matche un glob, `-size +Nc` compare la taille en octets, `-perm`
matche le mode, et `-type f` restreint aux fichiers réguliers. `find` est récursif
par défaut, il voit donc les fichiers nichés dans les sous-répertoires.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/

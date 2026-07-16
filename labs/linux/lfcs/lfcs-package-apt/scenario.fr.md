# Contexte — gestion de paquets Debian avec apt

Sur un système Debian/Ubuntu, les paquets sont gérés par **apt** (haut niveau) et
**dpkg** (bas niveau). Tu dois installer un outil, puis le **figer** pour qu'une
mise à niveau du système ne le change pas — et savoir dire de quel paquet provient
un fichier donné.

Ta mission, sur la VM Ubuntu :

1. Installe le paquet **`tree`** : `sudo apt-get install -y tree`.
2. **Fige**-le pour qu'`apt upgrade` l'ignore : `sudo apt-mark hold tree`.
3. Sache identifier le paquet propriétaire d'un fichier :
   `dpkg -S /usr/bin/tree` renvoie `tree`.

L'idée : `apt-get install`/`remove` gèrent les paquets avec leurs dépendances,
`apt-mark hold` fige la version d'un paquet, `apt-mark showhold` liste les paquets
figés, et `dpkg -S <fichier>` / `dpkg -l` interrogent ce que dpkg connaît — les
équivalents Debian de `dnf` et `rpm -qf`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/

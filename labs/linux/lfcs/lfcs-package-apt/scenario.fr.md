# Contexte — gestion de paquets Debian avec apt

Sur un système Debian ou Ubuntu, les paquets sont gérés par **apt** (haut niveau)
et **dpkg** (bas niveau). Tu dois installer un outil, puis le **figer** pour
qu'une mise à niveau du système ne le change pas, et savoir dire de quel paquet
provient un fichier donné.

L'idée : apt gère les paquets avec leurs dépendances et sait figer la version
d'un paquet pour qu'une mise à niveau ne la touche pas ; dpkg, en dessous, sait
dire à quel paquet appartient un fichier. Ce sont les pendants Debian de `dnf` et
de `rpm`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/

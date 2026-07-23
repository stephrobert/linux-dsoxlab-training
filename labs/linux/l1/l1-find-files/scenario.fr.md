# Contexte — trouver ce qu'il faut dans une arborescence de projet

Tu as reçu `projet.tar.gz`, un petit répertoire de projet. Sans ouvrir les
fichiers un par un, utilise **`find`** pour localiser exactement ce qui compte :
les logs, les gros fichiers, et ceux aux permissions privées.

L'idée : `find` parcourt toute une arborescence, récursivement, et sait filtrer
sur autre chose que le nom. Reste à savoir quel critère demander pour chaque
question, et comment l'exprimer.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/

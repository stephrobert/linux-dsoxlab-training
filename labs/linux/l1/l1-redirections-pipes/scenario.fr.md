# Contexte — trier un journal avec le shell seul

Tu as `journal.log`, un petit journal applicatif. Sans aucun éditeur, avec
uniquement des redirections et des pipes, tu dois extraire quelques faits dans
des fichiers séparés : combien de lignes, lesquelles sont des erreurs, ce
qu'affiche une commande qui échoue sur la sortie d'erreur, et à quoi ressemble
la sortie complète d'une commande (standard + erreur) fusionnée.

Ta mission — produire, dans le répertoire de travail :

1. `total.txt` — le nombre de lignes de `journal.log`.
2. `erreurs.txt` — uniquement les lignes `ERROR`.
3. `stderr.txt` — le message d'erreur d'une commande qui échoue (par exemple lire
   un fichier absent).
4. `tout.txt` — la sortie standard **et** la sortie d'erreur d'une commande,
   fusionnées dans un seul fichier.

Le piège : `>` ne capture que la sortie standard. Une erreur part sur la sortie
d'erreur et lui échappe, sauf si tu utilises `2>` ou `2>&1`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/

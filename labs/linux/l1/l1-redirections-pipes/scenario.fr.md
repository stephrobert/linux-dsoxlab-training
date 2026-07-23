# Contexte — trier un journal avec le shell seul

Tu as `journal.log`, un petit journal applicatif. Sans aucun éditeur, avec
uniquement des redirections et des pipes, tu dois extraire quelques faits dans
des fichiers séparés : combien de lignes, lesquelles sont des erreurs, ce
qu'affiche une commande qui échoue sur la sortie d'erreur, et à quoi ressemble
la sortie complète d'une commande (standard + erreur) fusionnée.

Le piège : une redirection ordinaire ne capture que la sortie standard. Une
erreur emprunte un autre canal et lui échappe. Viser ce second canal et le
fusionner avec le premier sont deux gestes distincts.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/

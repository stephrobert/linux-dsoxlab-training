# Contexte — empaqueter des fichiers avec tar

Tu as trois fichiers, `rapport.txt`, `config.yaml` et `notes.txt`, et tu dois les
transformer en archives, les inspecter, puis en ressortir un seul fichier sans
tout dépaqueter. C'est le pain quotidien des sauvegardes et des transferts.

L'idée : `tar` ne fait que regrouper, et la compression est un service qu'il
délègue à un compresseur externe, gzip ou bzip2 selon ce qu'on lui demande.
Créer, lister, extraire, choisir la destination et n'extraire qu'un seul membre
sont autant d'usages du même outil.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/

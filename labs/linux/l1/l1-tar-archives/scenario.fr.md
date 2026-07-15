# Contexte — empaqueter des fichiers avec tar

Tu as trois fichiers — `rapport.txt`, `config.yaml`, `notes.txt` — et tu dois les
transformer en archives, les inspecter, puis en ressortir un seul fichier sans
tout dépaqueter. C'est le pain quotidien des sauvegardes et des transferts.

Ta mission — produire, dans le répertoire de travail :

1. `docs.tar.gz` — une archive **gzip** des trois fichiers.
2. `liste.txt` — le **listing** du contenu de cette archive.
3. `extrait/rapport.txt` — **uniquement** `rapport.txt`, extrait dans un
   répertoire `extrait/` (extraction sélective).
4. `docs.tar.bz2` — une archive **bzip2** des mêmes trois fichiers.

L'idée : `tar` regroupe, `z`/`j` choisissent le compresseur (gzip/bzip2), `t`
liste, `x` extrait, et `-C` choisit où — et on peut extraire un seul membre en
le nommant.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/

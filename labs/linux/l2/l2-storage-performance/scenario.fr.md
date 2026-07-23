# Contexte — arrêter de gaspiller des I/O sur les dates d'accès

`/srv/data` sert une charge très sollicitée en lecture. Par défaut, Linux met à
jour la **date d'accès** (atime) de chaque fichier à la lecture, ce qui
transforme les lectures en écritures et dégrade les performances. Le correctif
standard est l'option de montage **`noatime`**. Ta mission : l'appliquer —
maintenant et durablement.

L'idée : les options de montage règlent le comportement d'un filesystem ;
`noatime` supprime les mises à jour d'atime. Reste à savoir comment le rendre
actif tout de suite **et** persistant au redémarrage : ce sont deux gestes
distincts.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/

# Contexte — apprendre un nouveau dépôt à dnf

Les logiciels viennent de quelque part. Quand un paquet n'est pas dans les dépôts
par défaut, il faut apprendre à `dnf` où le chercher, en lui déclarant un dépôt
supplémentaire. Fais-le bien : un identifiant clair, une vraie `baseurl`, le
dépôt activé, et **vérifié GPG** pour que les paquets soient authentifiés.

L'idée : un dépôt se décrit dans un fichier de configuration au format INI, une
`[section]` par dépôt. La vérification des signatures est le défaut de sécurité :
on ne la désactive pas pour se simplifier la vie. Reste à trouver où déposer ce
fichier, et comment demander à dnf de confirmer qu'il a bien pris le dépôt en
compte.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

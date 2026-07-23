# Contexte — le réseau statique façon Ubuntu : netplan

Debian et Ubuntu décrivent le réseau dans des fichiers YAML **netplan** sous
`/etc/netplan/`. Tu as besoin d'une adresse fixe et d'une route statique sur une
interface dédiée, et il faut que les deux reviennent après un reboot.

Tu travailles sur l'interface dédiée `lab0`. **Ne touche jamais à l'interface de
gestion**, celle qui porte ta route par défaut : c'est ton lien vers la machine.

L'idée : netplan est déclaratif, on décrit l'état voulu en YAML au lieu
d'enchaîner des commandes `ip`. Écrire le fichier ne suffit pas : tant qu'il n'a
pas été rendu vers le backend réseau, rien ne change sur la machine. Et se
tromper de contenu sur une machine distante, c'est perdre la main dessus.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/

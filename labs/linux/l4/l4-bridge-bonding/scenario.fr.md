# Contexte — agréger deux liens pour la redondance

Deux liens réseau doivent se comporter comme un seul, avec bascule : si l'actif
tombe, l'autre prend le relais. C'est un **bond** en mode `active-backup`, avec
`miimon=100`. Par-dessus se pose un **bridge**, la couche où s'attacheraient VMs
ou conteneurs. Construis les deux avec NetworkManager, sur des interfaces
dédiées, et rends l'ensemble persistant.

Tu travailles sur `dummy1`, `dummy2`, `bond0` et `br0`. **Ne touche jamais à
l'interface de gestion**, celle qui porte ta route par défaut : c'est ton lien
vers la machine.

L'idée : un bond agrège des liens (`active-backup` = redondance, un seul actif à
la fois, `miimon` sonde l'état du lien), et un bridge se pose au-dessus pour
offrir un domaine L2 unique. NetworkManager conserve chacun comme un profil de
connexion sur disque, et c'est ce profil qui fait survivre le montage au reboot.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/

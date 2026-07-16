# Contexte — agréger deux liens pour la redondance

Deux liens réseau doivent se comporter comme un seul, avec bascule : si l'actif
tombe, l'autre prend le relais. C'est un **bond** en mode `active-backup`.
Par-dessus se pose un **bridge** — la couche où s'attacheraient VMs ou conteneurs.
Construis les deux avec NetworkManager, sur des interfaces dédiées, et rends-le
persistant.

Ta mission, sur la VM (travaille sur `dummy1`/`dummy2`/`bond0`/`br0`, **ne touche
jamais à l'interface de gestion** — gestion) :

1. Crée un bond **`bond0`**, mode **`active-backup`** avec `miimon=100`
   (`nmcli con add type bond ... bond.options "mode=active-backup,miimon=100"`).
2. Enrôle **deux** interfaces esclaves — `dummy1` et `dummy2`
   (`nmcli con add type dummy ... master bond0`).
3. Crée un bridge **`br0`** et fais de **`bond0` un port** de ce bridge
   (`nmcli con mod bond0 master br0 slave-type bridge`), puis active le tout.

L'idée : un bond agrège des liens (`active-backup` = redondance, un actif à la
fois, `miimon` sonde l'état du lien) ; un bridge se pose au-dessus pour offrir un
domaine L2 unique. NetworkManager stocke chacun comme un profil de connexion
persistant, qui survit au reboot. `/proc/net/bonding/bond0` montre le mode et les
esclaves ; `/sys/class/net/br0/brif/` liste les ports du bridge.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/

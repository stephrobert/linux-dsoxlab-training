# Agréger deux liens pour la redondance

## La situation

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
https://www.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/

## Ce qui est demandé

### Mission

Agrège deux liens : un bond `active-backup` avec deux esclaves, sous un bridge.

### Objectif (état attendu)

1. `bond0` est un bond en mode `active-backup`, esclaves `dummy1` + `dummy2`
   (`/proc/net/bonding/bond0`).
2. `br0` est un bridge et `bond0` est un de ses ports
   (`/sys/class/net/br0/brif/`).
3. Les profils de connexion persistent sur disque.

### Contraintes

- **Ne touche jamais à l'interface de gestion** — celle qui porte ta route par défaut. Travaille sur les interfaces dédiées.
- On lit l'état du bonding, les ports du bridge et les profils sur disque.

### Validation

```bash
dsoxlab check l4-bridge-bonding
```

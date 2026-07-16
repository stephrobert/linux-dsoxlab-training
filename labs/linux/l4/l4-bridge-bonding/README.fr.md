# Lab — agrégation bond + bridge avec nmcli

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-bridge-bonding`

## Rappel

[**Bond & bridge sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/)

Un **bond** agrège des interfaces ; `active-backup` garde un actif et l'autre en
secours, `miimon` sonde l'état du lien. Un **bridge** par-dessus donne un domaine
L2 unique. `nmcli con add type bond|dummy|bridge` + `bond.options` +
`master`/`slave-type` câblent le tout ; chaque profil de connexion persiste au
reboot. `/proc/net/bonding/bond0` et `/sys/class/net/br0/brif/` montrent le
résultat.

Travaille sur `dummy1`/`dummy2`/`bond0`/`br0`, jamais sur l'interface de gestion.

## Objectifs

- `bond0` est un bond en mode `active-backup` avec les esclaves `dummy1` + `dummy2` ;
- `br0` est un bridge et `bond0` est un de ses ports ;
- les profils de connexion persistent sur disque.

## Valider

```bash
dsoxlab check l4-bridge-bonding
```

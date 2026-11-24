# L'interface est configurée mais morte

## La situation

Une connexion nommée `lab-net` existe sur l'interface `lab1` avec une adresse
statique correcte, pourtant l'interface ne porte aucune IP et elle ne reviendra
pas après un reboot. Quelque chose cloche dans son état : trouve-le et ranime le
lien.

Tu travailles sur `lab1`. **Ne touche jamais à l'interface de gestion**, celle
qui porte ta route par défaut : c'est ton lien vers la machine.

L'idée : une connexion peut être entièrement configurée et pourtant ne rien
porter, et une connexion qui remonte aujourd'hui ne remontera pas forcément au
prochain boot. Ce sont deux états distincts, tous deux lisibles dans ce que
rapporte NetworkManager : à lire, pas à deviner.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/

## Ce qui est demandé

### Mission

`lab-net` sur `lab1` est configurée mais morte et ne survivra pas à un reboot.
Diagnostique et rétablis-la.

### Objectif (état attendu)

1. La connexion `lab-net` est `activated` (`nmcli -g GENERAL.STATE con show lab-net`).
2. `connection.autoconnect` = `yes` (persistance reboot).
3. `lab1` porte `198.51.100.10` en live.

### Contraintes

- **Ne touche jamais à l'interface de gestion** (lien de gestion). Travaille uniquement sur `lab1`.
- On lit l'état NetworkManager et l'interface active, pas ton historique.

### Validation

```bash
dsoxlab check l4-network-troubleshoot
```

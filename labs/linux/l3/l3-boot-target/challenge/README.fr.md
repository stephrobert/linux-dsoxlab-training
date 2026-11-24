# Un serveur démarre sans interface

## La situation

Quelqu'un a laissé cette machine avec une cible de démarrage **graphique** par
défaut — inutile sur un serveur, et un gaspillage de ressources. Reviens à un
démarrage texte multi-utilisateur.

L'idée : les **cibles** (targets) systemd sont des états de démarrage ;
`multi-user.target` est l'état serveur standard (réseau + services, sans GUI),
`graphical.target` ajoute un gestionnaire d'affichage. Le système en désigne une
comme cible par défaut, et c'est cette désignation, et elle seule, qui survit au
reboot.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/

## Ce qui est demandé

### Mission

La cible de démarrage par défaut est `graphical.target`. Remets-la en serveur.

### Objectif (état attendu)

1. `systemctl get-default` → **`multi-user.target`**.

### Contraintes

- `systemctl set-default`. La validation lit la **cible réelle**, pas la commande.

### Validation

```bash
dsoxlab check l3-boot-target
```

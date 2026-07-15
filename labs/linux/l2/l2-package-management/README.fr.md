# Lab — gestion de paquets avec dnf

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-package-management`

## Rappel

[**dnf sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/)

`dnf install <pkg>` ajoute un paquet et ses dépendances ; `dnf remove <pkg>` le
retire ; `dnf list installed` et `rpm -q <pkg>` interrogent ce qui est présent.
`rpm -ql <pkg>` liste les fichiers d'un paquet.

## Objectifs

- installer `tree` ;
- retirer `zip` ;
- confirmer avec `rpm -q`.

## Valider

```bash
dsoxlab check l2-package-management
```

# Lab — gestion de paquets Debian (apt/dpkg)

> Préparer : `dsoxlab provision` puis `dsoxlab run lfcs-package-apt`

## Rappel

[**apt sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/)

`apt-get install|remove` gère les paquets et leurs dépendances ; `apt-mark hold`
fige une version pour qu'`apt upgrade` l'ignore (`apt-mark showhold` liste les
holds) ; `dpkg -l <paquet>` montre l'état d'installation ; `dpkg -S <fichier>` dit
quel paquet possède un fichier. Ce sont les pendants Debian de `dnf` / `rpm -qf`.

## Objectifs

- `tree` est installé ;
- `tree` est figé (`apt-mark showhold`) ;
- `dpkg -S /usr/bin/tree` renvoie `tree`.

## Valider

```bash
dsoxlab check lfcs-package-apt
```

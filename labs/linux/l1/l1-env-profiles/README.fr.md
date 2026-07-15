# Lab — variables d'environnement et fichier env sourcé

> Prépare l'espace : `dsoxlab run l1-env-profiles`

## Rappel

[**Variables d'environnement sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/)

`NOM=valeur` définit une variable de shell ; `export NOM` la publie pour que les
processus enfants en héritent. `source fichier` exécute un fichier dans le shell
*courant* (ses `export` persistent donc), contrairement à l'exécuter. Préfixer
`PATH` (`export PATH="$PWD/bin:$PATH"`) fait primer un répertoire local sur les
outils système.

## Objectifs

Écris `env.sh` pour qu'après `source env.sh` :

- `PROJET=dsoxlab` (exporté) ;
- `EDITOR=vim` (exporté) ;
- `GREETING="Bienvenue sur $PROJET"` ;
- `PATH` commence par `$PWD/bin`.

## Valider

```bash
dsoxlab check l1-env-profiles
```

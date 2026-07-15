# Lab — récupérer un filesystem plein

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-disk-space-troubleshoot`

## Rappel

[**Espace disque sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/)

`df -h` liste les filesystems et leur occupation ; `du -h --max-depth=1 <dir>`
montre ce que pèse chaque sous-répertoire, pour descendre jusqu'au coupable. Si
`df` dit plein mais `du` n'est pas d'accord, `lsof +L1` trouve un fichier
supprimé mais encore ouvert, tenu par un processus.

## Objectifs

Sur `/srv/data` plein :

- trouve le gros consommateur (`df`, puis `du`) ;
- supprime le superflu (le cache boursouflé) pour repasser **sous 50 %** ;
- conserve `/srv/data/app.log` et laisse le filesystem monté.

## Valider

```bash
dsoxlab check l2-disk-space-troubleshoot
```

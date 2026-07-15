# Lab — ACL POSIX

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-acl-posix`

## Rappel

[**ACL sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/)

`setfacl -m u:<user>:<droits> <chemin>` ajoute une entrée utilisateur nommé,
`g:<groupe>:` une entrée groupe nommé. Sur un répertoire, `d:` (ou `-d`) pose une
ACL **par défaut** dont les nouveaux fichiers héritent. `getfacl <chemin>`
affiche toutes les entrées ; `setfacl -b` les retire ; `ls -l` montre un `+`
final sur les fichiers porteurs d'ACL.

## Objectifs

- `carol` → `rw` sur `/srv/projet/report.txt` ;
- `auditors` → `rx` sur `/srv/projet` ;
- ACL par défaut : `auditors` → `r` sur les nouveaux fichiers de `/srv/projet`.

## Valider

```bash
dsoxlab check l2-acl-posix
```

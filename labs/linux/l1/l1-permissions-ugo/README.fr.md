# Lab — permissions de fichiers avec chmod

> Prépare l'espace : `dsoxlab run l1-permissions-ugo`

## Rappel

[**Modifier les droits sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/)

Chaque fichier a trois triplets de permissions — propriétaire, groupe, autres —
avec lecture (4), écriture (2), exécution (1). `chmod` les pose en octal
(`chmod 640 fichier`) ou en symbolique (`chmod g+r,o-r fichier`). Un répertoire a
besoin du bit `x` pour être traversé. Moindre privilège : accorde exactement ce
dont le fichier a besoin, pas plus.

## Objectifs

- `secret.txt` → `0600` (privé).
- `deploy.sh` → `0750` (exécutable propriétaire/groupe).
- `notes.txt` → `0640` (lisible par le groupe).
- `prive/` → répertoire `0700`.

## Valider

```bash
dsoxlab check l1-permissions-ugo
```

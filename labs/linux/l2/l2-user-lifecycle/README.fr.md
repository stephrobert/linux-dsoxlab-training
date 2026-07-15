# Lab — créer un compte local

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-user-lifecycle`

## Rappel

[**Utilisateurs et groupes sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/)

`useradd -u <uid> -m -d <home> -s <shell> -g <primaire> -G <secondaire> <nom>`
crée un compte avec une identité complète. Un utilisateur a **un seul groupe
primaire** (`-g`) et un nombre quelconque de **groupes secondaires** (`-G`).
Ensuite, `usermod -aG <groupe> <user>` ajoute un groupe — le `-a` est vital, sans
lui tu remplaces tous les groupes secondaires. `id` et `getent passwd`
inspectent le résultat.

## Objectifs

Crée `alice` :

- UID `1500`, home `/home/alice`, shell `/bin/bash` ;
- groupe primaire `staff` ;
- groupe secondaire `developers`.

## Valider

```bash
dsoxlab check l2-user-lifecycle
```

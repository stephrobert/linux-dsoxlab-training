# Challenge — l1-env-profiles

## Mission

Écris `env.sh` dans `challenge/work/`. Une fois sourcé, il configure
l'environnement du projet.

## Contrat (après `source env.sh`)

1. `PROJET` exporté = `dsoxlab`.
2. `EDITOR` exporté = `vim`.
3. `GREETING` = `Bienvenue sur dsoxlab` (construit à partir de `$PROJET`).
4. `PATH` commence par `$PWD/bin`.

## Contraintes

- `export` pour publier les variables, `$PWD/bin` en tête de `PATH`.
- La validation **source** ton fichier dans un sous-shell et lance un enfant pour
  vérifier l'export réel. Ne touche pas à ton vrai `~/.bashrc`.

## Validation

```bash
dsoxlab check l1-env-profiles
```

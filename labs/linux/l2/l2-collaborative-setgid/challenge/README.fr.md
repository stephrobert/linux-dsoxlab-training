# Un répertoire partagé qui partage vraiment

## La situation

Le groupe `devteam` (alice, bob) a besoin d'un répertoire commun, `/srv/partage`,
où chacun dépose des fichiers que **tout le groupe** peut ensuite modifier. Pour
l'instant il appartient à `root:root` et chaque fichier créé garde le groupe *de
son auteur* — donc la collaboration casse. La solution : le **bit set-GID** sur le
répertoire.

L'idée : sur un **répertoire**, le bit set-GID fait que tout nouveau fichier
dedans hérite du groupe du répertoire au lieu du groupe primaire de son créateur —
la condition pour qu'un dossier partagé soit vraiment collaboratif.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/

## Ce qui est demandé

### Mission

Fais de `/srv/partage` un répertoire collaboratif pour le groupe `devteam` avec le
bit set-GID.

### Objectif (état attendu)

1. `/srv/partage` est un répertoire de groupe `devteam`.
2. Son mode est `2775` (set-GID + `rwxrwxr-x`).
3. Un fichier créé dedans par un membre de `devteam` hérite du groupe `devteam`.

### Contraintes

- Le groupe `devteam` et les membres `alice`/`bob` existent déjà.
- On lit le mode/groupe du répertoire et on crée un fichier témoin en tant
  qu'`alice` pour vérifier le groupe hérité.

### Validation

```bash
dsoxlab check l2-collaborative-setgid
```

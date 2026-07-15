# Publier une version de linux-dsoxlab-training

**Language:** [English](./RELEASING.md) · [Français](./RELEASING.fr.md)

Ce dépôt livre du **contenu de labs**, pas un paquet Python. Une version publie
un **bundle `tar.gz`** du catalogue de labs comme asset d'une Release GitHub :
pas de PyPI, pas de wheel, aucun registre d'artefacts externe.

## Ce que contient une version

Le workflow `release.yml` construit `linux-dsoxlab-training-<version>.tar.gz`
avec :

- `labs/`, `meta.yml`, `conftest.py`, `solution/`, `ssh/` (clé publique seule)
- les documents de gouvernance (`README`, `LICENSE`, `CONTRIBUTING`,
  `CODE_OF_CONDUCT`, `SECURITY`, `CHANGELOG`)

Il **exclut** le pilotage local (`.claude/`, `todo/`, `ROADMAP-*.md`,
`CLAUDE.md`), les fichiers générés (`.venv/`, caches) et la **clé SSH privée**.
Une empreinte `.sha256` est publiée à côté de l'archive.

## Produire une version

1. Mettre à jour `CHANGELOG.md` et `CHANGELOG.fr.md` (basculer les entrées sous
   une nouvelle version).
2. S'assurer que `dsoxlab validate-structure` est vert en local.
3. Taguer et pousser le tag — cela déclenche `release.yml` :

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. Le workflow construit le `tar.gz`, son `.sha256`, et crée la Release GitHub
   avec des notes générées automatiquement.

## Vérifier une version

```bash
sha256sum -c linux-dsoxlab-training-<version>.tar.gz.sha256
tar tzf linux-dsoxlab-training-<version>.tar.gz | head
```

> Les commits et les tags sont créés par un humain, jamais par un assistant.

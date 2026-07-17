# Publier une version de linux-dsoxlab-training

**Language:** [English](./RELEASING.md) · [Français](./RELEASING.fr.md)

Ce dépôt livre du **contenu de labs**, pas un paquet Python. Une version publie
un **bundle `tar.gz`** du catalogue de labs comme asset d'une Release GitHub :
pas de PyPI, pas de wheel, aucun registre d'artefacts externe.

## Ce que contient une version

Le workflow `release.yml` construit `linux-dsoxlab-training-<version>.tar.gz`
avec :

- `labs/`, `meta.yml`, `conftest.py`, `solution/` (chiffré par vault)
- les documents de gouvernance (`README`, `LICENSE`, `CONTRIBUTING`,
  `CODE_OF_CONDUCT`, `SECURITY`, `CHANGELOG`)

Il **exclut** le pilotage local (`.claude/`, `todo/`, `ROADMAP-*.md`,
`CLAUDE.md`) et les fichiers générés (`.venv/`, caches). `ssh/` n'est **pas**
empaqueté du tout : le dossier entier est gitignored (il contient la paire de
clés du lab générée par `make bootstrap`), il n'existe donc jamais dans un
checkout CI.

Quatre artefacts accompagnent l'archive :

| Artefact | Rôle |
| --- | --- |
| `<pkg>.tar.gz.sha256` | empreinte d'intégrité |
| `provenance.intoto.jsonl` | provenance SLSA (ce que lit Scorecard Signed-Releases) |
| `<pkg>.tar.gz.cosign.bundle` | bundle de signature Cosign keyless |
| (côté registre) | attestation de build native GitHub |

## Produire une version

1. Mettre à jour `CHANGELOG.md` et `CHANGELOG.fr.md` (basculer les entrées sous
   une nouvelle version).
2. S'assurer que `dsoxlab validate-structure` est vert en local.
3. Taguer et pousser le tag — cela déclenche `release.yml` :

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. Le workflow construit le `tar.gz`, atteste sa provenance, le signe en keyless
   et crée la Release GitHub avec des notes générées automatiquement.

## Vérifier une version

Intégrité et contenu :

```bash
sha256sum -c linux-dsoxlab-training-<version>.tar.gz.sha256
tar tzf linux-dsoxlab-training-<version>.tar.gz | head
```

Provenance du build : prouve que l'archive a bien été produite par le workflow de
ce dépôt, et non reconstruite par quelqu'un d'autre.

```bash
gh attestation verify linux-dsoxlab-training-<version>.tar.gz \
  --repo stephrobert/linux-dsoxlab-training
```

Signature Cosign keyless. Les **deux** options sont obligatoires : sans elles,
`cosign verify-blob` accepte n'importe quelle identité, ce qui vide la
vérification de son sens.

```bash
cosign verify-blob \
  --bundle linux-dsoxlab-training-<version>.tar.gz.cosign.bundle \
  --certificate-identity-regexp "https://github.com/stephrobert/linux-dsoxlab-training/.github/workflows/release.yml@.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  linux-dsoxlab-training-<version>.tar.gz
```

> **Piège de version Cosign.** La CI installe **Cosign 3.x** (nouveau format de
> bundle). Un **Cosign 2.x** local répond `no signatures found` sur une archive
> pourtant parfaitement signée : la release n'est pas cassée, c'est l'outil local
> qui ne sait pas lire le format. Vérifiez `cosign version` et alignez-le avant
> de conclure quoi que ce soit.

> Les commits et les tags sont créés par un humain, jamais par un assistant.

# linux-dsoxlab-training : labs de sécurité Linux (RHCSA + LFCS)

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/linux-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/linux-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/linux-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/linux-dsoxlab-training)
[![Conformité Plumber](https://score.getplumber.io/github.com/stephrobert/linux-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/linux-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![Licence : CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Formation pratique **sécurité Linux et DevSecOps**, pilotée par la CLI
[`dsoxlab`](https://github.com/stephrobert/dsoxlab). Ce dépôt est le **catalogue
de labs** de la formation Linux du site
[blog.stephane-robert.info](https://blog.stephane-robert.info/docs/admin-serveurs/linux/),
orienté vers les certifications **RHCSA (EX200 v10)** et **LFCS**, avec un angle
de durcissement systématique.

## Ce que c'est

`linux-dsoxlab-training` est un **dépôt de contenu**, pas une application. Il
propose :

- des **labs guidés** avec des instructions précises,
- des **challenges** sans pas-à-pas, pour vérifier l'autonomie,
- des **capstones** qui synthétisent un bloc entier,
- une **validation automatique** qui prouve l'état du système (et non qu'une
  commande a été tapée),
- un **scoring** avec des indices à coût variable.

La CLI `dsoxlab` est le seul point d'entrée : elle démarre un lab, affiche les
instructions, valide, note et fait le bilan. Elle vit dans **son propre dépôt**
et s'installe **séparément** : elle ne fait pas partie de ce dépôt.

## Prérequis

- Python 3.11+ et [`uv`](https://docs.astral.sh/uv/)
- `git`
- Pour les labs L2+ (VM : systemd, pare-feu, SELinux, stockage), un provider
  parmi **KVM/libvirt**, **Incus** ou un cloud supporté (Outscale). Les labs
  shell (L1) ne demandent qu'un terminal.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/) : on
l'installe comme un outil autonome.

```bash
# 1. Installer la CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab        # ou : pipx install dsoxlab

# 2. Cloner ce catalogue de labs
git clone <url-de-ce-depot> linux-dsoxlab-training
cd linux-dsoxlab-training

# 3. Découvrir et lancer
dsoxlab list-labs
dsoxlab run <id-du-lab>
dsoxlab check <id-du-lab>
```

Vérifie ton environnement avec `dsoxlab doctor` (Python, pytest, runtimes, labs
détectés). Ce dépôt déclare plusieurs providers d'infrastructure : les labs VM
en exigent donc un actif.

```bash
dsoxlab use --provider kvm     # persisté pour ce dépôt
# ou, one-shot : DSOXLAB_PROVIDER=kvm dsoxlab provision
```

## Comment ça marche

### Le contrat déclaratif (deux niveaux)

Le catalogue est décrit par des données, pas par du code : le moteur `dsoxlab`
reste agnostique du domaine et lit deux niveaux de fichiers.

- **`meta.yml`** à la racine déclare l'identité du dépôt, la topologie
  d'infrastructure (réseau, hôtes, providers) et l'**ordre** des sections
  affiché par `list-labs`.
- **`lab.yaml`** par lab (sous `labs/linux/<section>/<lab>/`) déclare ses
  `skills`, son `level`, son `runtime` (shell/incus/kvm et hôte cible), ses
  `distros`, son `doc_url` et un bloc `validation` (`functional`, `security`,
  `persistence_after_reboot`). Un `lab.fr.yaml` optionnel surcharge le `title`
  et la `description` en français.

`dsoxlab validate-structure` vérifie tout le contrat : le `meta.yml` est
conforme, chaque lab référencé existe avec un `lab.yaml` valide, chaque
`runtime.host` pointe un hôte déclaré, et chaque fichier de test ou script
référencé est présent.

### Le cycle de vie d'un lab

L'apprenant pilote tout via la CLI ; un parcours type :

```bash
dsoxlab use --provider kvm            # choisir un provider d'infra (labs VM)
dsoxlab list-labs                     # parcourir le catalogue
dsoxlab show <id>                     # métadonnées et statut d'un lab
dsoxlab run <id>                      # préparer et démarrer l'environnement
dsoxlab course <id>                   # lire le cours guidé (optionnel)
dsoxlab challenge <id>                # lire la mission (sans pas-à-pas)
dsoxlab hint <id>                     # révéler un indice (déduit du score)
dsoxlab check <id>                    # lancer les tests, calculer et noter
dsoxlab submit <id>                   # soumission finale, ferme la session
dsoxlab progress                      # progression par bloc, score moyen
```

C'est `run` qui monte l'environnement. Pour un lab **shell**, il crée le
`workdir` du lab et copie les fixtures déclarées. Pour un lab **VM**, il
sélectionne l'hôte cible (provisionné par Terraform) et applique la mise en
place du lab avec Ansible.

### Les runtimes

| Runtime | Backend | Ce qu'il apporte |
|---|---|---|
| `shell` | shell local | Exercices mono-hôte rapides (fichiers, texte, permissions). Sans coût de VM : les tests tournent sur ta propre machine et valident son état réel. |
| `incus` | conteneurs Incus | Environnements Linux isolés, à démarrage rapide. |
| `kvm` | Terraform + libvirt | VM complètes, le seul runtime capable de prouver le **reboot/la persistance** (systemd, pare-feu, SELinux, stockage). |

Les labs VM sont provisionnés une fois avec `dsoxlab provision` (Terraform) et
détruits avec `dsoxlab destroy`. Les providers (KVM/Incus/Outscale) sont
interchangeables et choisis par dépôt via `dsoxlab use --provider <nom>` ; les
IP sont attribuées par le provider, jamais codées en dur.

### Le modèle de validation

La validation **prouve l'état du système, elle ne fait pas confiance à
l'apprenant**. Chaque lab embarque des tests `pytest`/`pytest-testinfra` sous
`challenge/tests/` qui vérifient des faits sur la machine : le service tourne
**et** est activé, le montage est présent **et** déclaré dans `/etc/fstab` par
UUID, le contexte SELinux est posé de façon persistante. Un test qui vérifie
seulement qu'une commande a été tapée est rejeté.

- En CI / mode formateur, une fixture du `conftest.py` racine **rejoue la
  solution de référence** (`solution/`) avant les tests, pour prouver que la
  solution elle-même est correcte.
- Dans `dsoxlab check` (le parcours apprenant), ce rejeu est **désactivé**
  (`LAB_NO_REPLAY=1`) : les tests valident le travail de l'apprenant.
- La **persistance après reboot** est un critère de premier ordre : c'est
  précisément ce qui fait échouer les candidats RHCSA, donc un lab VM qui
  configure quelque chose censé survivre à un reboot le vérifie explicitement.

### Scoring, indices, progression

`check` enregistre un score (tests réussis/total, moins le coût des indices
utilisés). Les indices sont **à coût variable** : en révéler un déduit des
points, d'où leur caractère opt-in. L'historique vit dans une base SQLite locale
(`~/.local/share/dsoxlab/progress.db`, surchargeable via XDG) ; `dsoxlab scores`
et `dsoxlab progress` la lisent. La session active (contexte, provider) est
stockée par dépôt dans `.dsoxlab-context.json`.

## Catalogue

Les labs vivent sous `labs/linux/` et sont ordonnés par `meta.yml` :

| Bloc | Sujet | Runtime |
|---|---|---|
| **L1** | Fondamentaux : shell, fichiers, exploration (validés sur l'état réel) | shell |
| **L2** | Stockage et sécurité : swap, LUKS, RAID, durcissement | VM |
| **depanner** | Dépannage : services, démarrage, journaux | VM |
| **capstones** | Examens blancs RHCSA/LFCS | VM |

## Contribuer et licence

- Contribuer : voir [CONTRIBUTING](./CONTRIBUTING.fr.md).
- Conduite : [Code de conduite](./CODE_OF_CONDUCT.fr.md) · Sécurité : [SECURITY](./SECURITY.fr.md).
- Versions : [RELEASING](./RELEASING.fr.md) (bundles tar.gz, pas de PyPI).
- Licence : [CC BY 4.0](./LICENSE).

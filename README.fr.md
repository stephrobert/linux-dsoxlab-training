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

### Garder à jour

De nouveaux labs arrivent dans ce dépôt, et la CLI évolue de son côté. Mets à
jour chacun séparément :

```bash
git pull                       # récupère les labs nouveaux/mis à jour dans ton clone
uv tool upgrade dsoxlab        # met à jour la CLI (ou : pipx upgrade dsoxlab)
```

Tes réponses en cours vivent dans le `challenge/work/` de chaque lab, qui est
gitignoré — `git pull` apporte donc les nouveaux labs sans jamais toucher à ton
travail.

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
dsoxlab doctor                        # vérifier l'environnement (Python, pytest, runtimes, labs)
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

Les labs vivent sous `labs/linux/` et sont ordonnés par `meta.yml`. La table
ci-dessous est générée à partir des vrais `lab.yaml` : lance
`python3 scripts/gen_catalog.py` pour la rafraîchir.

<!-- LABS:START -->
### Fondamentaux (l1)

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `l1-discover-linux-map` | Cartographier Linux : noyau, distribution et répertoires clés | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/) |
| `l1-choose-distro` | Choisir sa distribution Linux de référence | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions-serveur/) |
| `l1-prepare-vm` | Identifier sa machine Linux | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/) |
| `l1-first-terminal` | Premiers pas dans le terminal | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/prompt-terminal/) |
| `l1-read-a-command` | Lire et décoder une commande | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/anatomie-commande/) |
| `l1-get-help` | Obtenir de l'aide en ligne de commande | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/obtenir-aide/) |
| `l1-linux-filesystem` | Hiérarchie du système de fichiers Linux (FHS) | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/arborescence-fhs/) |
| `l1-navigate-filesystem` | Naviguer dans le système de fichiers | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/) |
| `l1-paths-absolute-relative` | Chemins absolus et relatifs | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/chemins-linux/) |
| `l1-redirections-pipes` | Rediriger les flux et chaîner des commandes avec des pipes | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/) |
| `l1-grep-regex` | Filtrer un journal avec grep et les expressions régulières | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/) |
| `l1-text-processing` | Transformer et agréger du texte avec cut, sort, uniq, sed et awk | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/traiter-texte/cut-tr-paste/) |
| `l1-tar-archives` | Archiver, compresser et extraire sélectivement avec tar, gzip et bzip2 | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/) |
| `l1-permissions-ugo` | Poser les permissions exactes avec chmod (octal et symbolique) | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/) |
| `l1-links-hard-sym` | Créer des liens physiques et symboliques et les distinguer | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/) |
| `l1-bash-script` | Écrire un premier script Bash : variables, boucle et condition | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/scripts-bash/premier-script/) |
| `l1-git-basics` | Initialiser un dépôt Git : commit, historique et branche | l1 | shell | [guide](https://blog.stephane-robert.info/docs/developper/version/git/bases-git/) |
| `l1-env-profiles` | Variables d'environnement : export, PATH et un fichier env sourcé | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/) |
| `l1-ssl-certificates` | Inspecter un certificat TLS avec openssl | l1 | shell | [guide](https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/) |

### Exploiter + Maintenir (l2)

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `l2-swap-management` | Ajouter et gérer le swap | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/) |
| `l2-fstab-persist-uuid` | Monter un filesystem de façon persistante par UUID dans /etc/fstab | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/) |
| `l2-partition-gpt` | Créer des partitions GPT sur un disque avec parted | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/) |
| `l2-filesystem-create-xfs` | Créer et labelliser un filesystem XFS, puis le monter | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/) |
| `l2-disk-space-troubleshoot` | Diagnostiquer un filesystem plein et récupérer de l'espace | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/) |
| `l2-storage-performance` | Optimiser un montage avec noatime (de façon persistante) | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/) |
| `l2-lvm-extend-persist` | Étendre un volume logique et prouver que le montage survit au reboot | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/) |
| `l2-nfs-mount-persist` | Monter un export NFS de façon persistante depuis un serveur | l2 | vm | [guide](https://blog.stephane-robert.info/docs/services/stockage/nfs/) |
| `l2-autofs-ondemand` | Monter un filesystem à la demande avec autofs | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/) |
| `l2-raid-mdadm` | Construire un RAID 1 logiciel avec mdadm | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/) |
| `l2-luks-encryption` | Chiffrer un disque avec LUKS | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/) |
| `l2-user-lifecycle` | Créer un compte local avec UID, shell et groupes exacts | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/) |
| `l2-password-policy` | Appliquer une politique d'expiration et de complexité des mots de passe | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/) |
| `l2-sudo-delegation` | Déléguer des droits sudo limités via un drop-in sudoers | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/) |
| `l2-acl-posix` | Accorder un accès fin avec les ACL POSIX | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/) |
| `l2-package-management` | Installer, supprimer et interroger des paquets avec dnf | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/) |
| `l2-repo-configure` | Configurer un dépôt dnf avec un fichier .repo | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/) |

### Services + Dépannage (l3)

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `l3-boot-target` | Régler la cible de démarrage systemd par défaut | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/) |
| `l3-service-create-unit` | Créer et activer un service systemd | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/) |
| `l3-service-diagnose` | Diagnostiquer et corriger un service systemd en crash loop | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/service-ne-demarre-pas/) |
| `l3-journald-persist` | Rendre le journal systemd persistant au reboot | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/) |
| `l3-scheduling-cron` | Planifier une tâche récurrente avec cron | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/) |
| `l3-app-constraints` | Régler les limites de ressources par utilisateur (fichiers ouverts) avec limits.d | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/) |
| `l3-sysctl-persist` | Durcir des paramètres noyau durablement avec sysctl.d | l3 | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/) |
| `l3-process-signals-priority` | Abaisser la priorité d'ordonnancement d'un service avec Nice | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/comprendre-processus/) |
| `l3-tuned-profile` | Appliquer un profil de performance tuned | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/) |
| `l3-fs-readonly-recover` | Récupérer un montage en lecture seule dû à un fstab cassé | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/) |
| `l3-ssh-access-recovery` | Réparer une config sshd cassée avant qu'elle ne te verrouille dehors | l3 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/) |

### Capstones

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `rhcsa-mock-exam` | Examen blanc RHCSA EX200 — 20 tâches sur 2 VMs | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/certifications/rhcsa/) |

_48 labs — table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contribuer et licence

- Contribuer : voir [CONTRIBUTING](./CONTRIBUTING.fr.md).
- Conduite : [Code de conduite](./CODE_OF_CONDUCT.fr.md) · Sécurité : [SECURITY](./SECURITY.fr.md).
- Versions : [RELEASING](./RELEASING.fr.md) (bundles tar.gz, pas de PyPI).
- Licence : [CC BY 4.0](./LICENSE).

---
applyTo: "**/*"
description: "Transformer linux-training en DevSecOps XL Labs — plateforme de formation pratique auto-portée, pilotée par une CLI Python, en relation avec https://blog.stephane-robert.info/docs/"
---

# linux-training — Instructions de transformation du projet

Ce document guide l'évolution du dépôt `linux-training`.

Le projet ne doit plus être pensé comme un simple ensemble de TP numérotés.
La cible est **DevSecOps XL Labs** (éponyme du binaire `dsoxlab`) : une plateforme
de formation pratique auto-portée qui accompagne les formations du site
**https://blog.stephane-robert.info/docs/**

Elle couvre plusieurs domaines : Linux, conteneurs, Kubernetes, IaC, sécurité,
CI/CD. Chaque lab est lié à un guide du site et expose une compétence précise,
validable automatiquement.

La plateforme propose :

- des **labs guidés**,
- des **challenges**,
- des **checklists**,
- des **capstones**,
- des **validations automatiques**,
- une **CLI Python unique** pour tout piloter.

La roadmap technique de référence est `ROADMAP-RUNTIMES.md`.
La roadmap pédagogique est `ROADMAP-LINUX.md` (dans `test-astro-5`).

---

## 1. Positionnement cible du dépôt

Le dépôt `linux-training` devient la couche pratique officielle de **DevSecOps XL Labs**,
plateforme multidomaine (Linux, conteneurs, Kubernetes, IaC, sécurité, CI/CD) liée au site
**https://blog.stephane-robert.info/docs/**

Il doit couvrir :

- la préparation des labs,
- leur exécution,
- leur validation,
- leur nettoyage,
- la progression par parcours,
- les capstones,
- les examens blancs à terme.

Le site reste la couche :

- cours,
- orientation,
- parcours,
- certification.

Le dépôt devient la couche :

- labs,
- challenge,
- validation,
- entraînement,
- capstone,
- preuve.

---

## 2. Règles structurantes non négociables

### 2.1 Une CLI Python unique pilote le projet

Le dépôt doit converger vers une **CLI Python** comme point d'entrée unique.

Ne pas construire un projet reposant sur une collection de scripts shell
indépendants sans point d'entrée cohérent.

Les scripts shell restent autorisés uniquement comme :

- helpers runtime,
- wrappers d'outils système,
- ou couches techniques très ciblées.

Mais l'orchestration globale doit passer par Python.

### 2.2 Le projet doit rester portable

Ne jamais coder en dur un chemin personnel dans le code.

Utiliser :

- `LAB_HOME` comme variable de référence,
- `~/Projets/lab-linux` comme valeur par défaut recommandée,
- `pathlib.Path` pour manipuler les chemins.

Le dépôt doit fonctionner même si l'utilisateur change :

- son home,
- sa racine de lab,
- son backend,
- son environnement local.

### 2.3 Réorganiser avant de réécrire

Le dépôt actuel contient déjà une base utile :

- dossiers `tp-*`,
- `README`,
- `challenge`,
- tests `pytest` / `pytest-testinfra`.

Ne pas jeter cette base.

La migration doit :

- préserver ce qui existe,
- introduire des conventions stables,
- créer une couche d'abstraction,
- puis migrer progressivement vers la structure cible.

### 2.4 Les labs doivent être pilotés par les compétences

Un lab ne doit pas exister juste parce qu'un guide existe.

Chaque lab doit prouver une capacité observable.

Exemples :

- manipuler des permissions correctement,
- diagnostiquer un service cassé,
- rendre un montage persistant,
- réduire l'exposition réseau,
- vérifier un état système après reboot.

### 2.5 Les validations testent des compétences, pas des artefacts fragiles

Les tests doivent valider :

- un état attendu,
- un mécanisme,
- un invariant,
- une capacité observable.

Éviter les assertions trop fragiles sur :

- une valeur arbitraire,
- un prénom codé en dur,
- une version ultra figée quand ce n'est pas le vrai objectif,
- un artefact trop spécifique qui ne mesure pas la compétence réelle.

### 2.6 Exécution terminal stable en Remote-SSH

Pour toute commande shell longue, multi-étapes, sensible à l'environnement, ou utilisant `set -e`, utiliser le format suivant :

```bash
bash --noprofile --norc -lc 'set -e; ...'
```

Ne pas lancer directement `set -e && ...` dans le terminal intégré si une exécution isolée est possible.
Si le même type de commande doit être rejoué, préférer le wrapper local `scripts/copilot-stable-shell.sh`.

---

## 3. Cible d'architecture

Le projet doit converger vers cette structure :

```text
linux-training/
├── README.md
├── pyproject.toml
├── ROADMAP-RUNTIMES.md     ← roadmap technique CLI + runtimes
├── src/
│   └── dsoxlab/              ← package Python principal
│       ├── cli.py
│       ├── config.py
│       ├── i18n/           ← traductions EN (défaut) + FR
│       ├── models/
│       ├── services/
│       ├── sessions/       ← persistance SQLite (.dsoxlab.db)
│       ├── runtimes/
│       ├── validators/
│       ├── discovery/
│       ├── reporting/
│       └── utils/
├── docs/
│   ├── parcours.md
│   ├── niveaux.md
│   ├── lfcs.md
│   ├── rhcsa.md
│   └── convention-labs.md
├── labs/
│   ├── linux/
│   │   ├── l1/
│   │   ├── l2/
│   │   ├── lfcs/
│   │   └── rhcsa/
│   └── capstones/
└── .github/
    ├── copilot-instructions.md
    ├── ISSUE_TEMPLATE/
    └── workflows/
````

### Règle de migration

Les anciens dossiers `tp-*` peuvent être conservés temporairement, mais le dépôt
doit converger vers une navigation centrée sur :

* `labs/linux/l1/`
* `labs/linux/l2/`
* `labs/linux/lfcs/`
* `labs/linux/rhcsa/`
* `labs/capstones/`


## 4. Choix techniques à privilégier

### 4.1 Langage et outillage

Utiliser **Python** comme langage principal.

Recommandations :

* Python moderne avec annotations de types,
* `pyproject.toml`,
* point d'entrée CLI installé via script console,
* code organisé sous `src/`.

### 4.2 CLI

La CLI doit être écrite en Python.

Préférer une bibliothèque adaptée à une CLI ergonomique.
Une structure de type `Typer` est un bon choix si elle simplifie :

* l'auto-documentation,
* les sous-commandes,
* la validation d'arguments,
* l'expérience développeur.

### 4.3 Rendu terminal

Une sortie lisible est attendue.

Utiliser une bibliothèque comme `rich` pour :

* statuts,
* tableaux,
* messages d'erreur,
* progression,
* synthèse de validation.

### 4.4 YAML et métadonnées

Les labs doivent être décrits par un fichier `lab.yaml`.

Le parsing YAML doit être fiable.
Préférer une bibliothèque Python adaptée à un travail propre sur YAML.

### 4.5 Tests

Conserver et renforcer :

* `pytest`
* `pytest-testinfra`

Les tests du projet doivent couvrir :

* la structure des labs,
* le parsing des métadonnées,
* la découverte des labs,
* les commandes CLI,
* les validations principales.

---

## 5. Contrat de la CLI

La CLI est le centre du projet.

Binaire : **`dsoxlab`** (installé via `uv pip install -e .` depuis `pyproject.toml`).

### 5.1 Sous-commandes implémentées ✔

```bash
dsoxlab use linux/l1 [--lang fr]    # contexte actif + langue
dsoxlab quit                         # efface le contexte
dsoxlab list-labs                    # liste filtrée
dsoxlab show <id>                    # détail d'un lab
dsoxlab run <id>                     # démarre l'environnement
dsoxlab hint <id>                    # indice (déduit points)
dsoxlab check <id>                   # tests + score + SQLite
dsoxlab scores                       # historique
dsoxlab reset <id>                   # remet à zéro
dsoxlab clean <id>                   # détruit les ressources
dsoxlab validate-structure           # vérifie tous les lab.yaml
dsoxlab doctor [--fix]               # diagnostique + remédiation
dsoxlab fullhelp                     # guide complet multilingue
```

### 5.2 Sous-commandes planifiées (P4+)

```bash
dsoxlab init-lab <id>        # squelette d'un nouveau lab
dsoxlab migrate-tp           # convertit les anciens tp-* en labs canoniques
dsoxlab capstone run <id>    # lance un capstone
dsoxlab capstone check <id>  # valide un capstone
dsoxlab export-index         # exporte l'index JSON
```

### 5.3 Règles UX

Chaque commande doit :

* avoir une aide claire,
* retourner un code de sortie fiable,
* afficher un message compréhensible,
* distinguer erreur utilisateur, erreur système et lab incomplet.

---

## 6. Modèle de données attendu

Chaque lab canonique doit suivre ce contrat minimal :

```text
<lab>/
├── lab.yaml
├── README.md
├── scenario.md
├── runtime/
│   ├── shell.sh
│   ├── incus.sh
│   └── kvm.sh
├── challenge/
│   ├── README.md
│   └── tests/
│       ├── test_functional.py
│       ├── test_security.py
│       └── test_persistence.py
├── fixtures/
├── evidence/
└── cleanup.sh
```

### 6.1 Champs obligatoires de `lab.yaml`

* `id`
* `title`
* `level`
* `skills`
* `runtime.type`
* `distros`
* `doc_url`
* `validation`

### 6.2 Exemple de structure attendue

```yaml
id: l2-03-systemd-persistance
title: Persister un service systemd après modification
level: l2
track:
  - maintenir
  - rhcsa
skills:
  - systemd
  - service-management
  - journald
  - persistence-after-reboot
difficulty: intermediate
estimated_time: 45m
runtime:
  type: kvm
  topology: single-vm
distros:
  - debian12
  - ubuntu24.04
  - rhel10
doc_url: https://blog.stephane-robert.info/docs/admin-serveurs/linux/services/
validation:
  functional: true
  security: true
  persistence_after_reboot: true
certification_tags:
  - rhcsa
  - lfcs
```

### 6.3 Contrat métier

Un lab doit toujours pouvoir exposer :

* sa capacité visée,
* son niveau,
* son runtime,
* sa topologie,
* sa distribution,
* son lien avec le site,
* son mode de validation.

---

## 7. Stratégie runtime

### 7.1 Niveaux de runtime

* `shell` pour les labs simples sans vraie pile système
* `incus` comme runtime de transition
* `kvm` comme cible pour les labs système réels, les capstones et les certifications

### 7.2 Politique de migration

`Incus` est toléré comme runtime transitoire.

Mais les nouveaux labs stratégiques doivent cibler **KVM**.

Priorité de bascule vers KVM :

1. paquets système
2. services
3. persistance
4. stockage
5. réseau
6. sécurité
7. certification
8. capstones

### 7.3 Abstraction obligatoire

Le code Python ne doit pas disperser partout des appels directs aux runtimes.

Créer une couche d'abstraction claire, par exemple :

* `RuntimeManager`
* `ShellRuntime`
* `IncusRuntime`
* `KvmRuntime`

Le reste de l'application ne doit pas dépendre directement des détails
d'implémentation du backend.

---

## 8. Architecture Python recommandée

### 8.1 Modules attendus

Le code Python est organisé autour de responsabilités claires (tous implémentés) :

* `cli.py` : point d'entrée CLI (Typer + `_I18nGroup`)
* `config.py` : lecture de config, `LAB_HOME`, `ActiveContext`, `.dsoxlab-context.json`
* `i18n/` : `get_lang()`, `_()`, traductions `en.py` + `fr.py`
* `models/` : `LabDefinition`, `RuntimeConfig`, `ValidationConfig`, `HintFile`
* `discovery/` : découverte des labs (`labs/` + fallback `tp-*`)
* `services/` : orchestration métier (`get_lab`, `run_lab`, `check_lab`, …)
* `sessions/` : persistance SQLite (`.dsoxlab.db`) — scores et hints
* `runtimes/` : `BaseRuntime`, `ShellRuntime`, `IncusRuntime`, `KvmRuntime`, `RuntimeManager`
* `validators/` : validation structure et métadonnées
* `reporting/` : synthèses terminal Rich (`print_*` functions)
* `utils/` : wrapper subprocess centralisé (`run_command`)

### 8.2 Typage

Le code Python doit être typé.

Attendus :

* annotations de types partout où c'est utile,
* signatures explicites,
* structures de données claires,
* éviter les dictionnaires non typés propagés partout.

### 8.3 Manipulation des chemins

Utiliser `pathlib.Path`.

Ne pas concaténer des chemins à la main.

### 8.4 Exécution de commandes

Centraliser l'exécution de commandes système.

Créer un wrapper unique pour :

* lancer une commande,
* capturer stdout/stderr,
* gérer le timeout,
* journaliser,
* remonter des erreurs propres.

---

## 9. État d'avancement de la migration

### P1 — Stabilisation minimale ✔ DONE

* CLI Python `dsoxlab` opérationnelle
* Découverte des labs `labs/` + fallback `tp-*`
* `LAB_HOME` comme variable de référence
* `lab.yaml` introduit sur les premiers labs

### P2 — Couche d'abstraction ✔ DONE

* Modules Python complets (`models/`, `runtimes/`, `services/`, `validators/`, `reporting/`, `utils/`)
* `RuntimeManager` + `ShellRuntime` + `IncusRuntime` + `KvmRuntime`
* `validate-structure`, `doctor` implémentés

### P3 — Scoring, hints, persistance ✔ DONE

* Système de hints avec coûts (`challenge/hints.yaml`)
* Score calculé : `points - sum(hint costs)`
* Persistance SQLite (`.dsoxlab.db`) : tables `results` + `hint_requests`
* Commandes `hint`, `check`, `scores` implémentées

### P3+ — i18n complète, doctor --fix, fullhelp ✔ DONE

* CLI entièrement traduite via `src/dsoxlab/i18n/` (EN défaut, FR disponible)
* Labs bilingues : `lab.yaml` (EN) + `lab.fr.yaml` (surcharges titre/description)
* `doctor --fix` : remédiation automatique des composants manquants
* `fullhelp` : guide complet multilingue
* Binaire renommé `dxsol` → **`dsoxlab`**
* IDs de labs en anglais (ex : `l1-01-files-navigation`)

### P4 — Commandes utilitaires ⏳ PLANIFIÉ

* `init-lab`, `migrate-tp`, `export-index`
* Templates d'issues GitHub

### P5 — CI / GitHub Actions ⏳ PLANIFIÉ

* Validation de structure automatique
* Tests CLI dans la CI
* Détection des labs incomplets

### P6 — Certification et capstones ⏳ PLANIFIÉ

* Labs LFCS, labs RHCSA
* Premiers capstones officiels
* Validations post-reboot
* Examens blancs

---

## 10. Règles quand Copilot modifie le code

### 10.1 Toujours préserver la compatibilité de migration

Quand une ancienne structure existe encore, ne pas la casser sans prévoir :

* un adaptateur,
* une compatibilité temporaire,
* ou une migration explicite.

### 10.2 Favoriser le code simple et lisible

Préférer :

* petites fonctions,
* responsabilités claires,
* messages d'erreur utiles,
* objets métier explicites.

Éviter :

* les fonctions géantes,
* les effets de bord implicites,
* la logique shell noyée partout dans le Python,
* les chemins codés en dur.

### 10.3 Toujours relier technique et pédagogie

Une décision technique doit servir une capacité pédagogique.

Exemple :

* un champ `validation.persistence_after_reboot` sert à savoir si un lab doit tester la persistance ;
* un champ `track` sert à relier le lab à un parcours ;
* un champ `certification_tags` sert à l'intégration LFCS/RHCSA.

### 10.4 Préserver l'expérience apprenant

Les commandes et la structure du dépôt doivent rester compréhensibles.

Le projet n'est pas seulement un outil pour l'auteur.
C'est aussi une base qui doit pouvoir être relue, maintenue et comprise.

### 10.5 Toujours synchroniser l'aide CLI et le fullhelp

Toute modification d'une commande (ajout, suppression, renommage, nouveaux
options) doit être répercutée **simultanément** dans :

* le texte d'aide de la commande (`help=_("...")` dans `cli.py`),
* les clés i18n correspondantes dans `en.py` **et** `fr.py`,
* la section `fullhelp_commands` dans `en.py` **et** `fr.py`,
* les clés de messages qui référencent la commande (ex : `context_active`).

Ne jamais laisser le `fullhelp` décrire une commande qui n'existe plus,
ni omettre une commande ou option nouvellement ajoutée.

---

## 11. README et documentation interne

Le README racine doit évoluer pour décrire un produit, pas juste des TP.

Il doit expliquer :

* ce qu'est `linux-training`,
* le rôle de la CLI,
* la structure des labs,
* le rôle de `LAB_HOME`,
* les runtimes,
* la logique des parcours,
* la validation,
* le lien avec le site de formation.

Les fichiers dans `docs/` doivent documenter :

* les parcours,
* les niveaux,
* la convention des labs,
* LFCS,
* RHCSA.

---

## 12. Contrat minimal de qualité

Le dépôt doit converger vers une qualité minimale mesurable.

### 12.1 Structure

Tout lab incomplet doit être détectable.

### 12.2 Métadonnées

Tout `lab.yaml` invalide doit être signalé.

### 12.3 CLI

Toute commande principale doit être testée.

### 12.4 Runtime

Les erreurs runtime doivent être remontées proprement.

### 12.5 Validation

La distinction entre validation fonctionnelle, sécurité et persistance doit être claire.

---

## 13. Conventions i18n — règles pour les développeurs

### 13.1 Règle fondamentale

Tout texte affiché à l'utilisateur doit passer par `_("key")`.

Ne jamais mettre de chaîne hardcodée dans `cli.py` ou `reporting/console.py`.

### 13.2 Ajouter une nouvelle clé

1. Ajouter la clé **dans les deux fichiers** : `en.py` et `fr.py` simultanément.
2. Utiliser le commentaire de section correspondant (`# ── cmd … ──`).
3. Tester avec `DSOXLAB_LANG=fr dsoxlab <commande>` et `DSOXLAB_LANG=en dsoxlab <commande>`.

### 13.3 Labs bilingues

* `lab.yaml` = source canonique, **en anglais**, toujours présente.
* `lab.fr.yaml` = surcharges FR pour `title` et `description` uniquement.
* **Ne jamais mettre** d'autres champs dans `lab.fr.yaml` (ils seraient ignorés).

### 13.4 IDs de labs

* Les IDs et noms de répertoires sont **toujours en anglais**.
* Format : `<level>-<nn>-<slug-anglais>` (ex : `l1-01-files-navigation`).
* Les anciens TP en français (`tp-01-navigation-fichiers`) sont tolérés temporairement
  mais doivent être migrés via `migrate-tp` (P4).

---

## 14. Anti-patterns à éviter

Ne pas :

* reconstruire tout le dépôt d'un coup,
* jeter les anciens TP sans stratégie de transition,
* coder en dur `~/Projets/lab-linux` partout,
* faire dépendre toute la logique d'Incus,
* mettre la logique métier dans des scripts shell opaques,
* créer une CLI sans typage ni structure,
* laisser les métadonnées devenir facultatives,
* générer des labs sans lien explicite avec les guides du site,
* écrire des tests qui vérifient des artefacts arbitraires au lieu des compétences.

---

## 14. Résultat cible attendu

À terme, `linux-training` doit être capable de :

* découvrir les labs disponibles,
* afficher leurs métadonnées,
* lancer un lab selon son runtime,
* valider un lab,
* réinitialiser un lab,
* nettoyer un lab,
* signaler les labs incomplets,
* structurer la progression par niveaux et certifications,
* supporter les capstones,
* servir de moteur de preuve pour la formation Linux.


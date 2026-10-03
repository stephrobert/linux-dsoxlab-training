# Contribuer à linux-dsoxlab-training

**Language:** [English](./CONTRIBUTING.md) · [Français](./CONTRIBUTING.fr.md)

Ce dépôt est un **catalogue de labs** consommé par la CLI
[`dsoxlab`](https://github.com/stephrobert/dsoxlab). Les contributions sont de
nouveaux labs, des correctifs et des traductions. La CLI vit dans son propre
dépôt : n'ajoute pas de code moteur ici.

## Mise en place

```bash
uv tool install dsoxlab        # la CLI (outil externe)
git clone <url-de-ce-depot> linux-dsoxlab-training
cd linux-dsoxlab-training
dsoxlab doctor                 # vérifier l'environnement
```

## La règle d'or : la validation prouve l'état

Les tests d'un lab doivent vérifier **l'état du système**, jamais qu'une commande
a été tapée. Le service tourne **et** est activé ; le montage est présent **et**
déclaré dans `/etc/fstab` par UUID ; le contexte SELinux est posé de façon
persistante. Dès qu'un lab configure quelque chose censé survivre à un reboot,
les tests vérifient la **persistance après reboot** explicitement : c'est
précisément ce qui fait échouer les candidats RHCSA.

## Anatomie d'un lab

```text
labs/linux/<section>/<lab>/
├── lab.yaml            # le contrat (id, level, runtime, validation…)
├── lab.fr.yaml         # optionnel : surcharge FR du title/description UNIQUEMENT
├── README.md / scenario.md
├── setup.yaml / cleanup.yaml       # labs VM
└── challenge/
    ├── README.md       # la mission, sans pas-à-pas
    ├── hints.yaml      # indices à coût variable
    ├── tests/test_functional.py    # la preuve : l'état du système
    └── work/           # matériel de départ (labs shell)
solution/…              # solution de référence, rejouée en CI pour se prouver
```

## Proposer un lab

- **Partir d'une capacité, pas d'un guide.** Décris une capacité démontrable
  (« étendre un volume logique et prouver que le montage survit au reboot »),
  ouvre une issue, et cale le périmètre avant d'écrire.
- **Choisir le runtime qu'impose le sujet :** VM (`kvm`/`incus`) pour tout ce qui
  touche systemd, le pare-feu, SELinux, le démarrage ou le stockage persistant ;
  `shell` pour les fichiers, le texte et les permissions.
- Fais pointer `doc_url` vers le vrai guide que le lab fait pratiquer.

## Vérifications locales (avant d'ouvrir une PR)

```bash
dsoxlab validate-structure     # le contrat meta.yml + lab.yaml
dsoxlab check <id-du-lab>       # lancer les tests du lab (ou : pytest)
python3 scripts/gen_catalog.py # rafraîchir le catalogue du README (labs + URLs)
```

**Obligatoire avant chaque push :** le `README.md` racine et `README.fr.md`
doivent lister **tous** les labs avec l'**URL de leur guide compagnon**. Le
catalogue est généré à partir des vrais `lab.yaml` : lance
`python3 scripts/gen_catalog.py` après avoir ajouté ou renommé un lab, et
`python3 scripts/gen_catalog.py --check` pour vérifier. La CI et le hook
`pre-push` refusent tous deux un catalogue périmé.

### Attester un lab dans les deux sens

`python3 scripts/valider-labs.py --lab <id>` exige qu'un lab rende **0 avant
le travail** et **100 après la solution**, et écrit le verdict dans
`validation-labs.json`. Pour un lab VM, il ramène d'abord ses machines à une
**base figée** : sans cela, le premier check noterait aussi ce qu'ont laissé
les labs joués avant lui sur les mêmes VM.

Cette base se fige **une fois, sur des VM neuves**, et se refige après chaque
`provision`, qui recrée les domaines :

```bash
dsoxlab destroy --yes && dsoxlab provision
bash scripts/rebase-vms.sh     # environ 2 min ; un reset prend ensuite ~6 s
```

Sans base valide, le validateur refuse de jouer le lab et dit pourquoi.

## Conventions

- **Id de lab :** `<niveau>-<slug>` (ex. `l1-first-terminal`),
  identique au nom du répertoire.
- **Commits :** `feat(<lab>): …`, `fix: …`, `docs: …`, `test: …`.
- **i18n :** `lab.fr.yaml` surcharge le `title` et la `description` uniquement.

## Pull requests

Travaille sur une branche dédiée, garde `dsoxlab validate-structure` vert, écris
une description claire et relie la capacité/issue traitée.

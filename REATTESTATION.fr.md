# Réattester les labs de ce catalogue

> Page écrite le 2026-10-19, avec des valeurs **mesurées sur le disque** et non
> recopiées. Les chiffres vieillissent : le `validation-labs.json` reste la
> source de vérité pour les verdicts.

## Pourquoi cette page existe

Le 2026-10-19, une campagne de réattestation a inscrit **douze faux ROUGE** dans
un catalogue avant d'être arrêtée, et s'est bloquée vingt-trois minutes dans un
autre. Aucune des deux causes ne tenait aux labs : un `.venv` dont les shebangs
désignaient l'ancien nom du dépôt après son renommage, et un outil en ligne de
commande qui attendait un réseau que le bac à sable ne lui donnait pas.

Dans les deux cas, le validateur **avait l'air de mesurer les labs alors qu'il
mesurait sa propre panne**, et il l'écrivait dans le relevé. Un faux ROUGE coûte
plus cher qu'une absence de verdict : il envoie chercher un défaut dans un lab
qui n'en a pas.

## Ce que ce catalogue exige

- **dsoxlab 0.5.4 ou plus** dans le `PATH`. C'est la version du moteur qui sera inscrite dans le relevé, et le relevé la déclare pour TOUS les labs : voir la section sur le rejeu partiel.
- **`.vault-pass` à la racine** : 89 fichier(s) de solution de ce catalogue sont chiffrés par ansible-vault, et le cycle les pose déchiffrés. Le secret n'est jamais commité. Ici : présent.
- **Une infrastructure provisionnée** : 69 lab(s) sont en `runtime: vm` sur le réseau `lab-linux`, et exigent `dsoxlab provision` avant la campagne, `dsoxlab destroy` après. Les hôtes attendus sont `alma-rhcsa-1.lab`, `alma-rhcsa-2.lab`, `ubuntu-lfcs-1.lab`.
- De la mémoire libre réelle, et non celle qu'annonce `doctor` : détruire l'infra des autres dépôts AVANT de provisionner celle-ci, sinon les VM se disputent la RAM et les labs échouent par épuisement, ce qui ressemble à un défaut de lab.

### L'étape sans laquelle le validateur refuse de jouer

Ce catalogue isole ses labs par recouvrement qcow2 : chaque lab repart d'une VM
neuve, sans quoi chacun noterait l'état laissé par le précédent.
`scripts/rebase-vms.sh` fige cet état de départ, et **tout `dsoxlab provision`
l'invalide** : un provisionnement recrée les domaines avec un UUID neuf, et
libvirt refuse alors de restaurer l'ancien état mémoire.

La séquence est donc contrainte, dans cet ordre :

```bash
dsoxlab provision                  # les VM du meta.yml
bash scripts/rebase-vms.sh         # boot complet puis gel mémoire, quelques minutes
mise exec -- uv run scripts/valider-labs.py
dsoxlab destroy                    # en partant, pour libérer la RAM
```

**Sauter le rebase ne donne pas un faux vert, il donne un ROUGE qui parle
d'autre chose.** Mesuré le 2026-10-19 sur `bdd` : « isolation impossible :
db1.lab n'a pas de base figée ». Le message nomme le geste, mais un verdict
ROUGE inscrit dans le relevé se lit ensuite comme un défaut de lab, alors que
le lab n'a jamais été joué. C'est pour cette raison que ce relevé-là n'a pas
été commité.

Le rebase veut des VM **qui n'ont joué aucun lab** : juste après le
provisionnement, donc, et pas au milieu d'une campagne.

## La commande

```bash
uv run scripts/valider-labs.py
```

Un seul lab, pour éprouver le harnais avant d'engager les 89 :

```bash
uv run scripts/valider-labs.py --lab <id-du-lab>
```

**Commencer par un seul lab n'est pas une précaution de principe.** C'est ce qui
distingue un défaut d'environnement d'un défaut de lab : si le lab unitaire
passe, le harnais est sain ; s'il échoue comme les autres, c'est le harnais
qu'il faut réparer.

## L'état actuel

Relevé actuel : 89 VALIDE. Moteur déclaré : dsoxlab 0.4.1. Dates des verdicts : 2026-10-12, 2026-10-17. Durée cumulée du dernier cycle mesuré : **40 minutes** pour 89 labs, hors provisionnement et destruction d'infrastructure.

## Les quatre pièges qui produisent un faux verdict

**1. Un `.venv` au shebang mort.** Si le dépôt a été renommé, les scripts de
`.venv/bin/` pointent encore l'ancien chemin et ne s'exécutent plus. Le
symptôme est un échec identique sur chaque lab, souvent sur le déchiffrement de
la solution. Vérification et correctif :

```bash
head -1 .venv/bin/ansible-vault      # le chemin doit exister
uv venv --clear && uv sync           # le recréer
```

**2. `uv run --no-sync` sur un venv vide.** Le drapeau suppose un environnement
déjà peuplé. Sur un clone neuf, il rend un `ModuleNotFoundError` avant d'avoir
regardé un seul lab. Lancer sans `--no-sync` la première fois.

**3. Un outil qui attend un réseau que le bac à sable ne donne pas.** Mesuré
sur un `octl --version` resté bloqué vingt-trois minutes : seule la commande de
premier niveau est exemptée, un sous-processus ne l'est pas. Si une campagne
n'avance plus, regarder ses processus enfants avant de soupçonner un lab :

```bash
ps -eo pid,etimes,cmd | grep -E 'python.*valider[-]labs'
ps --ppid <pid-du-validateur> -o pid,etimes,cmd
```

**4. Un rejeu partiel rend l'en-tête du relevé faux.** La version du moteur est
enregistrée **une fois pour tout le fichier**, alors que les verdicts sont
individuels. Rejouer un seul lab réécrit donc cet en-tête, et le relevé affirme
que tous ses labs ont été attestés avec la version courante. Soit on rejoue tout,
soit on restaure le relevé :

```bash
git checkout -- validation-labs.json
```

## Ce que le relevé ne dit pas

Il ne dit pas **avec quelle version du moteur chaque lab** a été attesté, mais
seulement celle de la dernière campagne. C'est un manque connu, et il se voit
dès qu'une campagne est partielle.

Ce catalogue enregistre bien cet en-tête (`genere_le`, `dsoxlab` et la version des outils employés), ce qui est la bonne pratique de la collection.

## Pourquoi les verdicts de ce catalogue sont périmés

Un **seul** commit les a périmés, et il est vérifié plutôt que repris d'une liste : `6f25b79` du **2026-10-17**, « fix(labs): les messages d'échec en EN + FR, et une contrainte qu'aucun test ne tenait (#84) », qui touche **87 fichiers de tests**.

Ce n'est donc pas une dérive progressive : c'est une campagne coordonnée de bilinguisation des messages d'échec, menée le 2026-10-17 sur huit catalogues et 289 fichiers de tests. L'intitulé de ce commit nomme en outre un défaut corrigé au passage, et c'est lui qui rend le rejeu obligatoire : un test qui notait faux invalide le verdict qu'il a rendu.

À ne pas confondre avec le commit du 2026-10-19, qui a changé l'hôte des `doc_url` de `blog.` à `www.`. Celui-là touche des descripteurs et de la documentation, il ne change aucun geste et ne périme rien.

## Le format du relevé décide de ce que le site peut en dire

Le relevé de ce catalogue est au format **enveloppé**, et le site y lit bien la version du moteur, actuellement « dsoxlab 0.4.1 ».

Le générateur du site ne lit `genere_le` et `dsoxlab` **que si la clé `labs`
est un dictionnaire** : un relevé dont les clés de premier niveau sont
directement les identifiants de labs part dans une autre branche, qui rend une
date et un outil vides. Corriger le champ sans corriger le format ne servirait
donc à rien, et c'est pour ça que les deux sont dits ensemble ici.

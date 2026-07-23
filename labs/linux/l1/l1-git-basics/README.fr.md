# Lab — les bases de Git

## Rappel

[**Les bases de Git sur le guide compagnon**](https://blog.stephane-robert.info/docs/developper/version/git/bases-git/)

`git init` crée un dépôt, `git add <fichier>` indexe les changements,
`git commit -m` enregistre un instantané, `git log` montre l'historique, et
`git switch -c <nom>` (ou `git branch <nom>`) ouvre une branche. `git status` dit
ce qui n'est pas encore commité.

## Le cours

Les exemples ci-dessous construisent un dépôt de démonstration `carnet-demo/`
avec ses propres fichiers et sa propre branche : le challenge, lui, vous
demandera un autre dépôt, d'autres fichiers et une autre branche. Le but est
d'apprendre le cycle, pas de recopier une ligne.

Toutes les sorties affichées ici ont été produites sur une AlmaLinux 10 avec
**Git 2.52.0** et `LANG=en_US.UTF-8`. Deux choses varient d'une machine à
l'autre et changeront chez vous : les **empreintes de commit** (chaque commit
en obtient une différente) et la **langue des messages**, Git étant traduit en
français quand la locale l'est.

### Vérifier que Git est là, et lequel

Git n'est pas toujours installé : sur une machine fraîche, la commande n'existe
tout simplement pas.

```bash
git --version
```

```text
bash: git: command not found
```

Sur une distribution de la famille RHEL (AlmaLinux, Rocky, Fedora), le paquet
s'installe avec `dnf` :

```bash
sudo dnf install git
```

Sur Debian et Ubuntu, le guide donne l'équivalent `apt` :

```bash
sudo apt update
sudo apt install git
```

Une fois installé, relancez la vérification :

```bash
git --version
```

```text
git version 2.52.0
```

> **Regardez ce numéro avant de suivre un tutoriel.** `git switch` et
> `git restore`, utilisés plus bas, ne sont apparus qu'en **Git 2.23** (août
> 2019). Sur une machine plus ancienne, il faut se rabattre sur `git checkout`.

### Créer le dépôt avec `git init`

`git init <nom>` crée le dossier s'il n'existe pas et y installe la mécanique
de versionnage :

```bash
git init carnet-demo
cd carnet-demo
```

```text
hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Initialized empty Git repository in /home/ansible/carnet-demo/.git/
```

Deux enseignements dans cette sortie.

La dernière ligne confirme la création. Les lignes `hint:` ne sont **pas une
erreur** : Git prévient que la branche initiale s'appelle `master` faute de
réglage `init.defaultBranch`, et annonce que ce défaut passera à `main` en Git
3.0. Les deux noms sont fonctionnellement identiques. Retenez surtout qu'un
dépôt tout neuf n'a **pas forcément** la branche que vous croyez : demandez-le
plutôt que de le supposer.

```bash
git branch --show-current
```

```text
master
```

Le dossier créé est vide, à un détail près :

```bash
ls -a
```

```text
.
..
.git
```

Tout Git tient dans ce `.git/`. Le supprimer détruit l'historique.

```bash
ls -la .git/
```

```text
total 16
drwxr-xr-x. 6 ansible ansible  103 Jul 22 13:57 .
drwxr-xr-x. 3 ansible ansible   18 Jul 22 13:57 ..
-rw-r--r--. 1 ansible ansible   92 Jul 22 13:57 config
-rw-r--r--. 1 ansible ansible   73 Jul 22 13:57 description
-rw-r--r--. 1 ansible ansible   23 Jul 22 13:57 HEAD
drwxr-xr-x. 2 ansible ansible 4096 Jul 22 13:57 hooks
drwxr-xr-x. 2 ansible ansible   21 Jul 22 13:57 info
drwxr-xr-x. 4 ansible ansible   30 Jul 22 13:57 objects
drwxr-xr-x. 4 ansible ansible   31 Jul 22 13:57 refs
```

| Élément | Rôle |
|---|---|
| `HEAD` | pointe vers la branche courante |
| `config` | configuration propre à ce dépôt (niveau `--local`) |
| `objects/` | tous les objets Git : commits, arbres, contenus de fichiers |
| `refs/` | les pointeurs de branches et de tags |
| `hooks/` | scripts déclenchés automatiquement à certains événements |
| `info/` | exclusions locales et informations diverses |

`HEAD` n'est qu'un fichier texte d'une ligne :

```bash
cat .git/HEAD
```

```text
ref: refs/heads/master
```

Enfin, l'état d'un dépôt sans aucun commit :

```bash
git status
```

```text
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

À ce stade, `git branch` ne renvoie **rien du tout** : la branche n'existera
réellement qu'au premier commit, puisqu'une branche est un pointeur et qu'il
n'y a encore rien à pointer.

### Le cycle quotidien : modifier, indexer, commiter

Le guide résume tout Git en un schéma :

```text
  Modifier     →     Indexer     →     Commiter     →     Vérifier
 (éditeur)         (git add)         (git commit)         (git log)
```

Créez un fichier, puis demandez son état :

```bash
printf 'Carnet de bord de l atelier\n' > notes.txt
git status
```

```text
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	notes.txt

nothing added to commit but untracked files present (use "git add" to track)
```

`notes.txt` est **non suivi** (untracked) : Git le voit mais ne s'en occupe
pas. La forme courte dit la même chose en une ligne :

```bash
git status -s
```

```text
?? notes.txt
```

Deux colonnes : la gauche pour l'index, la droite pour le répertoire de
travail. `??` signale un fichier inconnu de Git, `A` un ajout indexé, `M` une
modification.

`git add` fait passer le fichier dans l'index, l'antichambre du prochain
commit :

```bash
git add notes.txt
git status -s
```

```text
A  notes.txt
```

Le `A` est en colonne gauche : le contenu est indexé, prêt à être enregistré.

### L'identité : Git refuse de commiter sans elle

Un commit porte le nom et l'adresse de son auteur. Sans eux, la commande
échoue :

```bash
git commit -m "Ajoute le carnet de bord"
```

```text
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: empty ident name (for <ansible@atelier.lab>) not allowed
```

La configuration de Git a trois niveaux, du plus large au plus précis, le plus
précis l'emportant :

| Niveau | Portée | Fichier | Option |
|---|---|---|---|
| system | tous les utilisateurs de la machine | `/etc/gitconfig` | `--system` |
| global | votre compte | `~/.gitconfig` | `--global` |
| local | ce dépôt seulement | `.git/config` | `--local` |

Sans option, `git config` écrit au niveau **local**, ce qui est exactement ce
qu'il faut pour un dépôt d'exercice : rien ne déborde sur le reste de la
machine.

```bash
git config user.name "Etudiant Demo"
git config user.email "etudiant@example.lab"
git config --list --show-origin | grep user
```

```text
file:.git/config	user.name=Etudiant Demo
file:.git/config	user.email=etudiant@example.lab
```

`--show-origin` indique le fichier d'où vient chaque valeur : c'est le moyen le
plus rapide de comprendre pourquoi un réglage n'est pas celui qu'on croyait.

Le commit passe maintenant :

```bash
git commit -m "Ajoute le carnet de bord"
```

```text
[master (root-commit) fc9cf0e] Ajoute le carnet de bord
 1 file changed, 1 insertion(+)
 create mode 100644 notes.txt
```

Cette ligne se lit ainsi : branche `master`, `root-commit` parce que c'est le
tout premier commit du dépôt (il n'a aucun parent), `fc9cf0e` l'empreinte
abrégée, puis le message. Chez vous l'empreinte sera différente : elle dépend
du contenu, de l'auteur et de la date.

```bash
git status
```

```text
On branch master
nothing to commit, working tree clean
```

### Exclure ce qui ne doit pas être versionné

Le fichier `.gitignore` liste ce que Git doit ignorer. Il se crée **avant** le
premier commit, pas après.

```bash
printf 'verifier les sauvegardes\nrelire le journal\n' > taches.txt
printf 'sortie temporaire\n' > sortie.log
printf '*.log\n' > .gitignore
git status -s
```

```text
?? .gitignore
?? taches.txt
```

`sortie.log` a disparu de la liste : le motif `*.log` l'exclut. Quelques
motifs courants :

| Motif | Correspond à |
|---|---|
| `*.log` | tous les fichiers terminant par `.log` |
| `build/` | le dossier `build` et tout son contenu |
| `/TODO` | le seul fichier `TODO` à la racine du dépôt |
| `!important.log` | exception : suivre ce fichier malgré `*.log` |

> **Ne committez jamais de secret.** Mots de passe, clés API, jetons,
> certificats : une fois dans l'historique, ils y restent, visibles de tous
> ceux qui ont accès au dépôt, même supprimés ensuite. Le `.gitignore` est la
> première barrière.

Avant de commiter, inspectez ce qui est sur le point d'être enregistré :

```bash
git add taches.txt .gitignore
git diff --staged
```

```text
diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..397b4a7
--- /dev/null
+++ b/.gitignore
@@ -0,0 +1 @@
+*.log
diff --git a/taches.txt b/taches.txt
new file mode 100644
index 0000000..d556b71
--- /dev/null
+++ b/taches.txt
@@ -0,0 +1,2 @@
+verifier les sauvegardes
+relire le journal
```

| Commande | Compare | Montre |
|---|---|---|
| `git diff` | répertoire de travail et index | ce qui n'est pas encore indexé |
| `git diff --staged` | index et dernier commit | ce qui sera commité |
| `git diff HEAD` | répertoire de travail et dernier commit | tout ce qui a bougé |

```bash
git commit -m "Ajoute la liste des taches et le gitignore"
```

```text
[master bc410a8] Ajoute la liste des taches et le gitignore
 2 files changed, 3 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 taches.txt
```

### Lire l'historique

```bash
git log
```

```text
commit bc410a8e63207e4a2fbd49a2806c9f7e6cc5203b
Author: Etudiant Demo <etudiant@example.lab>
Date:   Wed Jul 22 13:58:17 2026 +0000

    Ajoute la liste des taches et le gitignore

commit fc9cf0e0c61b9d8f91ac5905df9ad0e8e1e75aeb
Author: Etudiant Demo <etudiant@example.lab>
Date:   Wed Jul 22 13:58:11 2026 +0000

    Ajoute le carnet de bord
```

Du plus récent au plus ancien. Sur un long historique, la sortie passe dans un
pager : `q` pour en sortir.

La vue de tous les jours tient sur une ligne par commit :

```bash
git log --oneline
```

```text
bc410a8 Ajoute la liste des taches et le gitignore
fc9cf0e Ajoute le carnet de bord
```

> **Où sont les `(HEAD -> master)` des tutoriels ?** Git ne décore la sortie
> que lorsqu'elle va vers un terminal. Dans un tube ou une redirection, la
> décoration disparaît. Ajoutez `--decorate` pour la forcer :
> `git log --oneline --decorate` affiche
> `bc410a8 (HEAD -> master) Ajoute la liste des taches et le gitignore`.

Pour savoir quels fichiers chaque commit a touchés :

```bash
git log --stat --oneline
```

```text
bc410a8 Ajoute la liste des taches et le gitignore
 .gitignore | 1 +
 taches.txt | 2 ++
 2 files changed, 3 insertions(+)
fc9cf0e Ajoute le carnet de bord
 notes.txt | 1 +
 1 file changed, 1 insertion(+)
```

`git show` détaille un commit précis, `--stat` en limite l'affichage aux
fichiers :

```bash
git show --stat HEAD
```

```text
commit bc410a8e63207e4a2fbd49a2806c9f7e6cc5203b
Author: Etudiant Demo <etudiant@example.lab>
Date:   Wed Jul 22 13:58:17 2026 +0000

    Ajoute la liste des taches et le gitignore

 .gitignore | 1 +
 taches.txt | 2 ++
 2 files changed, 3 insertions(+)
```

Autres filtres utiles, tirés du guide : `git log --author="nom"`,
`git log --since="2 weeks ago"`, `git log -- chemin/fichier`,
`git log --grep="mot"` et `git log -S "texte"` qui retrouve le commit ayant
introduit ou retiré un morceau de code.

Enfin, la liste des fichiers réellement **suivis**, qui n'est pas la même chose
que la liste des fichiers présents sur le disque :

```bash
git ls-files
```

```text
.gitignore
notes.txt
taches.txt
```

### Ouvrir une branche

Une branche est un pointeur mobile vers un commit. Rien n'est copié :

```bash
git branch brouillon
ls -l .git/refs/heads/
```

```text
total 8
-rw-r--r--. 1 ansible ansible 41 Jul 22 13:58 brouillon
-rw-r--r--. 1 ansible ansible 41 Jul 22 13:58 master
```

41 octets chacune : l'empreinte du commit sur 40 caractères, plus le saut de
ligne. C'est tout ce qu'est une branche.

`git branch <nom>` crée le pointeur **sans** y basculer. L'astérisque marque
la branche courante :

```bash
git branch
```

```text
  brouillon
* master
```

Pour y aller :

```bash
git switch brouillon
```

```text
Switched to branch 'brouillon'
```

```bash
git branch --show-current
cat .git/HEAD
```

```text
brouillon
ref: refs/heads/brouillon
```

`HEAD` a suivi : il désigne toujours l'endroit où vous êtes.

Les deux gestes tiennent en une commande, `-c` pour create :

```bash
git switch -c essai
```

```text
Switched to a new branch 'essai'
```

> **`switch` ou `checkout` ?** `git switch -c <nom>` et
> `git checkout -b <nom>` font la même chose. `git checkout` est la syntaxe
> historique, mais il sert aussi à restaurer des fichiers, ce qui prête à
> confusion. Depuis Git 2.23, `git switch` ne fait que changer de branche.

Ce qui est commité sur une branche ne bouge pas l'autre. Un commit fait depuis
`brouillon` fait avancer ce seul pointeur :

```bash
git log --oneline --graph --all --decorate
```

```text
* f9b38b3 (HEAD -> brouillon) Note une idee a creuser
* bc410a8 (master) Ajoute la liste des taches et le gitignore
* fc9cf0e Ajoute le carnet de bord
```

`--all` montre toutes les branches, `--graph` dessine leur forme. De retour sur
`master`, le fichier modifié dans `brouillon` a retrouvé son contenu d'avant :
c'est tout l'intérêt d'une branche, isoler un travail.

Supprimer une branche fusionnée est immédiat, supprimer une branche qui porte
du travail unique est refusé :

```bash
git switch master
git branch -d essai
```

```text
Switched to branch 'master'
Deleted branch essai (was bc410a8).
```

```bash
git branch -d brouillon
```

```text
error: the branch 'brouillon' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D brouillon'
```

Ce refus est une protection : `-D` force et perd les commits qui n'existent
nulle part ailleurs.

### Savoir si l'arbre de travail est propre

« Propre » a un sens précis : rien de modifié, rien d'indexé en attente, aucun
fichier non suivi et non ignoré. La forme lisible par un script est
`git status --porcelain`, dont la sortie est **vide** quand tout est enregistré.

Avec une modification et un fichier nouveau en attente :

```bash
git status --porcelain
```

```text
 M taches.txt
?? memo.txt
```

La première ligne commence par une espace : la colonne de gauche (l'index) est
vide, seul le répertoire de travail a changé. Après avoir traité les deux
fichiers, la même commande ne réaffiche plus rien du tout, pas même une ligne
vide. C'est cette sortie nulle qui définit un arbre propre.

Notez que `git commit -am "..."` n'indexe que les fichiers **déjà suivis** :
un fichier nouveau resterait en `??`, donc l'arbre resterait sale. Pour un
nouveau fichier, il faut passer par `git add`.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `fatal: not a git repository (or any of the parent directories): .git` | vous n'êtes pas dans le dépôt : `cd` dedans, ou `git init` s'il n'existe pas |
| `bash: git: command not found` | le paquet n'est pas installé (`sudo dnf install git` ou `sudo apt install git`) |
| `fatal: empty ident name ... not allowed` | identité absente : `git config user.name` et `git config user.email` dans le dépôt |
| `fatal: your current branch 'master' does not have any commits yet` | le dépôt n'a encore aucun commit : `git add` puis `git commit` |
| `git add` ignore un fichier | il correspond à un motif du `.gitignore` : vérifiez-le, ou forcez avec `git add -f` |
| `git diff` ne montre rien alors que vous avez modifié | les modifications sont déjà indexées : `git diff --staged` |
| `error: the branch 'x' is not fully merged` | la branche porte des commits absents d'ailleurs : `-D` pour forcer, en connaissance de cause |
| `git init` répond `Reinitialized existing Git repository` | le dossier est déjà un dépôt : relancer `git init` est sans danger, mais inutile |
| `git branch` ne renvoie rien | dépôt sans aucun commit : la branche n'existe pas encore |

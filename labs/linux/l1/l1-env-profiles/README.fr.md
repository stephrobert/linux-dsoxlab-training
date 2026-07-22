# Lab — variables d'environnement et fichier env sourcé

## Rappel

[**Variables d'environnement sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/)

`NOM=valeur` définit une variable de shell ; `export NOM` la publie pour que les
processus enfants en héritent. `source fichier` exécute un fichier dans le shell
*courant* (ses `export` persistent donc), contrairement à l'exécuter. Préfixer
`PATH` fait primer un répertoire local sur les outils système.

## Le cours

Les exemples ci-dessous travaillent sur `~/demo-env`, un répertoire de
démonstration, avec un fichier `parametres.sh` et les variables `APPLI`,
`PAGER` et `BANNIERE` : le challenge, lui, vous demandera un autre fichier,
d'autres variables et d'autres valeurs. Le but est d'apprendre la méthode, pas
de recopier une ligne.

Toutes les sorties reproduites ici viennent d'une AlmaLinux 10, connectée en
tant qu'utilisateur `ansible`. Vos chemins personnels différeront.

### Lire une variable, lister l'environnement

Le `$` demande au shell de remplacer le nom par sa valeur. Sans lui, vous
n'obtenez que le texte :

```bash
echo $HOME
echo $USER
echo HOME
```

```text
/home/ansible
ansible
HOME
```

`env` liste l'environnement complet. Comme la sortie est longue, on la filtre :

```bash
env | grep "^PATH="
```

```text
PATH=/home/ansible/.local/bin:/home/ansible/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
```

### Variable de shell, ou variable d'environnement

C'est `export` qui fait la différence, et un processus enfant est le seul juge
fiable. On prépare le décor :

```bash
mkdir -p ~/demo-env/outils
cd ~/demo-env
```

Sans `export`, la variable ne quitte pas le shell courant :

```bash
APPLI="facturation"
echo "  shell courant : [$APPLI]"
bash -c 'echo "  enfant        : [$APPLI]"'
```

```text
  shell courant : [facturation]
  enfant        : []
```

Avec `export`, l'enfant la voit :

```bash
export APPLI="facturation"
bash -c 'echo "  enfant        : [$APPLI]"'
```

```text
  enfant        : [facturation]
```

L'héritage n'est pas limité à un seul niveau : un petit-fils de processus la
voit aussi, puisque chaque enfant transmet son environnement à son tour.

```bash
bash -c 'bash -c '\''echo "  petit-fils voit APPLI = [$APPLI]"'\'''
```

```text
  petit-fils voit APPLI = [facturation]
```

C'est aussi la différence que montre `env`, qui n'affiche **que** les variables
exportées :

```bash
LOCALE_SEULE="valeur"
env | grep -E "^(APPLI|LOCALE_SEULE)="
```

```text
APPLI=facturation
```

`LOCALE_SEULE` existe pourtant bien dans le shell courant : `echo
$LOCALE_SEULE` l'affiche. Elle est simplement absente de l'environnement.

> **Pas d'espace autour du `=`.** `APPLI = "facturation"` n'est pas une
> affectation : le shell y voit la commande `APPLI` suivie de deux arguments.
> La machine répond `bash: line 3: APPLI: command not found`.

`unset` fait le chemin inverse et supprime la variable :

```bash
export ESSAI="bonjour"; echo "  avant : [$ESSAI]"
unset ESSAI;            echo "  apres : [$ESSAI]"
```

```text
  avant : [bonjour]
  apres : []
```

### Réutiliser une variable dans une autre

Une variable peut être construite à partir d'une autre, à condition d'utiliser
les guillemets **doubles**. Les guillemets simples empêchent toute
substitution :

```bash
export ESSAI_DOUBLE="Session $APPLI ouverte"
export ESSAI_SIMPLE='Session $APPLI ouverte'
echo "  doubles : [$ESSAI_DOUBLE]"
echo "  simples : [$ESSAI_SIMPLE]"
```

```text
  doubles : [Session facturation ouverte]
  simples : [Session $APPLI ouverte]
```

La substitution a lieu **au moment de l'affectation**, pas à la lecture :
changer `APPLI` ensuite ne modifiera pas `ESSAI_DOUBLE`.

### PATH : l'ordre décide de la commande exécutée

`PATH` est une liste de répertoires séparés par `:`. Le shell les parcourt
**dans l'ordre** et s'arrête au premier qui contient la commande demandée.
Fabriquons un outil local :

```bash
cat > ~/demo-env/outils/inventaire <<'EOF'
#!/bin/bash
echo "inventaire : 42 machines"
EOF
chmod +x ~/demo-env/outils/inventaire
inventaire; echo "  code retour : $?"
```

Le répertoire n'étant pas dans `PATH`, la commande reste introuvable :

```text
bash: line 3: inventaire: command not found
  code retour : 127
```

Le code `127` est la signature de « commande introuvable » : retenez-le, il
distingue un problème de `PATH` d'un vrai échec du programme.

On met le répertoire en tête :

```bash
export PATH="$HOME/demo-env/outils:$PATH"
inventaire
which inventaire
```

```text
inventaire : 42 machines
/home/ansible/demo-env/outils/inventaire
```

Préfixer ou suffixer n'a rien d'équivalent. Avec un outil qui porte le nom
d'une commande système, la position tranche :

```bash
cat > ~/demo-env/outils/sort <<'EOF'
#!/bin/bash
echo "ceci est le sort local, pas celui du systeme"
EOF
chmod +x ~/demo-env/outils/sort
PATH="$PATH:$HOME/demo-env/outils" bash -c 'which sort'
PATH="$HOME/demo-env/outils:$PATH" bash -c 'which sort'
```

```text
/usr/bin/sort
/home/ansible/demo-env/outils/sort
```

> **Gardez toujours `$PATH` dans la nouvelle valeur.** `export PATH="/un/chemin"`
> sans `:$PATH` efface tous les répertoires système : plus aucune commande
> externe n'est trouvée dans ce terminal.

### Sourcer un fichier, ou l'exécuter

C'est le coeur du sujet. Écrivons un fichier de paramètres :

```bash
cat > ~/demo-env/parametres.sh <<'EOF'
export APPLI="facturation"
export PAGER="less"
export BANNIERE="Session $APPLI ouverte"
export PATH="$HOME/demo-env/outils:$PATH"
EOF
chmod +x ~/demo-env/parametres.sh
```

Si on l'**exécute**, rien ne subsiste :

```bash
./parametres.sh
echo "  APPLI apres execution : [$APPLI]"
echo "  BANNIERE             : [$BANNIERE]"
```

```text
  APPLI apres execution : []
  BANNIERE             : []
```

Si on le **source**, tout reste :

```bash
source ./parametres.sh
echo "  APPLI apres source    : [$APPLI]"
echo "  BANNIERE             : [$BANNIERE]"
echo "  1re entree de PATH    : ${PATH%%:*}"
```

```text
  APPLI apres source    : [facturation]
  BANNIERE             : [Session facturation ouverte]
  1re entree de PATH    : /home/ansible/demo-env/outils
```

La raison tient en un numéro de processus. Un script exécuté tourne dans un
**shell enfant**, qui disparaît en emportant ses variables ; un script sourcé
est lu par le shell **courant**. On le prouve avec `$$`, le PID du shell :

```bash
cat > ~/demo-env/qui-suis-je.sh <<'EOF'
#!/bin/bash
echo "  le script tourne dans le PID $$"
EOF
chmod +x ~/demo-env/qui-suis-je.sh
echo "  le shell courant est le PID $$"
./qui-suis-je.sh
source ./qui-suis-je.sh
```

```text
  le shell courant est le PID 11735
  le script tourne dans le PID 11751
  le script tourne dans le PID 11735
```

Exécuté, le script a son propre PID. Sourcé, il porte celui du shell appelant :
il n'y a pas eu de nouveau processus. Le raccourci de `source` est le point :
`. ./parametres.sh` fait exactement la même chose.

Dernière conséquence, utile au diagnostic : `chmod +x` ne sert qu'à
l'exécution. Un fichier destiné à être sourcé n'a pas besoin d'être exécutable.

```bash
printf 'export TEST_SOURCE=ok\n' > /tmp/sans-droit.sh
chmod 0644 /tmp/sans-droit.sh
source /tmp/sans-droit.sh; echo "  apres source : [$TEST_SOURCE]"
/tmp/sans-droit.sh; echo "  execution : code $?"
```

```text
  apres source : [ok]
bash: line 16: /tmp/sans-droit.sh: Permission denied
  execution : code 126
```

Retenez la paire : `126` veut dire « trouvé mais pas exécutable », `127` veut
dire « pas trouvé du tout ». Les confondre fait chercher un problème de `PATH`
là où il n'y a qu'un `chmod` manquant.

### Quel fichier Bash lit-il, et quand

Le guide compagnon *Personnaliser son shell* donne un tableau à trois lignes :
`~/.bash_profile` à la connexion, `~/.bashrc` à chaque terminal interactif,
`~/.profile` en remplacement du premier. Ce tableau est juste dans les grandes
lignes, mais il n'explique pas les cas qui font perdre le plus de temps. Deux
questions décident, et elles sont indépendantes :

- le shell est-il un **shell de login** (ouvert par une connexion) ?
- le shell est-il **interactif** (un humain tape dedans) ?

Ne devinez pas : demandez-le au shell lui-même. `shopt -q login_shell` répond à
la première, la présence d'un `i` dans `$-` répond à la seconde.

```bash
echo "\$- = [$-]   login_shell = $(shopt -q login_shell && echo on || echo off)"
```

Voici ce que répondent cinq situations différentes, mesuré sur la machine :

| Situation | `$-` | login | interactif |
|---|---|---|---|
| Session `ssh hôte` puis saisie au clavier | `himBHs` | on | oui |
| `ssh hôte 'commande'` | `hBc` | off | non |
| `bash -lc 'commande'` | `hBc` | on | non |
| `bash -c 'commande'` | `hBc` | off | non |
| `bash -ic 'commande'` | `hiBHc` | off | oui |

Un détail confirme le premier cas : dans une session ouverte par `ssh`, `echo
$0` affiche `-bash`, avec un tiret initial. Ce tiret est posé par le programme
qui ouvre la connexion, pas par l'option `-l` : `bash -lc 'echo $0'` répond
`bash` sans tiret bien qu'il soit un shell de login. Le tiret trahit donc une
vraie connexion, tandis que `shopt -q login_shell` répond à la question au sens
de Bash. Quand les deux divergent, c'est `shopt` qui décrit le comportement
observé plus haut.

Pour savoir **quels fichiers** sont réellement lus, la méthode qui ne ment pas
consiste à déposer une ligne `echo` en tête de chacun, puis à observer. Sur
cette AlmaLinux 10, les cinq situations donnent :

| Situation | Fichiers lus, dans l'ordre |
|---|---|
| Session `ssh hôte` interactive | `/etc/profile` (et `/etc/profile.d/*.sh`), `~/.bash_profile`, `~/.bashrc` |
| `ssh hôte 'commande'` | `~/.bashrc` **seul** |
| `bash -lc 'commande'` | `/etc/profile` (et `/etc/profile.d/*.sh`), `~/.bash_profile`, `~/.bashrc` |
| `bash -c 'commande'` | aucun |
| `bash -ic 'commande'` | `~/.bashrc`, puis `/etc/profile.d/*.sh` via `/etc/bashrc` |

Trois choses à retenir de ce tableau, et aucune n'est intuitive.

**Un `~/.bashrc` n'est pas lu parce que la session est interactive.** La
deuxième ligne le montre : `ssh hôte 'commande'` n'est ni un shell de login ni
un shell interactif, et pourtant `~/.bashrc` est lu, lui et lui seul. C'est le
cas de toutes les commandes distantes, donc de l'automatisation.

**`~/.bashrc` n'est jamais lu directement par un shell de login.** Il l'est
parce que `~/.bash_profile` le source explicitement. Sur cette machine, le
fichier livré par la distribution commence par :

```bash
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
```

Retirez ces quatre lignes et `~/.bashrc` cesse d'exister pour les connexions,
sans qu'aucun message ne le signale. Le `HOME` détourné de la section suivante
permet de le constater en deux commandes : avec la boucle `if`, la connexion
affiche les deux fichiers ; sans elle, elle n'affiche plus que
`~/.bash_profile`.

**`/etc/profile.d/*.sh` est lu dans bien plus de cas qu'il n'y paraît, mais en
silence.** Un `echo` déposé dans `/etc/profile.d/` ne s'affiche pas pour un
`bash -lc`, alors que le script est bien exécuté. La raison est dans
`/etc/profile` :

```bash
for i in /etc/profile.d/*.sh /etc/profile.d/sh.local ; do
    if [ -r "$i" ]; then
        if [ "${-#*i}" != "$-" ]; then
            . "$i"
        else
            . "$i" >/dev/null
        fi
```

Le test `"${-#*i}" != "$-"` demande si `$-` contient un `i`, donc si le shell
est interactif. Sinon, la sortie du script part à la poubelle. Pour trancher,
n'utilisez pas un `echo` mais une variable, qui survit à la redirection :

```bash
echo 'TRACE_PROFILED=1' | sudo tee /etc/profile.d/00-trace.sh
bash -lc 'echo "TRACE_PROFILED=[$TRACE_PROFILED]"' </dev/null
bash -c  'echo "TRACE_PROFILED=[$TRACE_PROFILED]"' </dev/null
```

```text
TRACE_PROFILED=[1]
TRACE_PROFILED=[]
```

Quant à la cinquième ligne du tableau, elle surprend : un `bash -ic` n'est pas
un shell de login, et il lit quand même `/etc/profile.d/`. C'est `/etc/bashrc`,
sourcé par `~/.bashrc`, qui s'en charge, avec le commentaire qui l'explique :

```bash
  if ! shopt -q login_shell ; then # We're not a login shell
    ...
    for i in /etc/profile.d/*.sh; do
```

Autrement dit, sur cette famille de distributions, `/etc/profile.d/` finit par
être lu quel que soit le chemin, du moment que le shell est de login ou
interactif.

### Le premier des trois gagne

Pour un shell de login, Bash cherche `~/.bash_profile`, puis `~/.bash_login`,
puis `~/.profile`, et s'arrête **au premier trouvé**. Les suivants ne sont
jamais lus. On peut le vérifier sans risque en détournant `HOME` vers un
répertoire jetable :

```bash
mkdir -p /tmp/bacasable
for f in .bash_profile .bash_login .profile; do
  printf 'echo "  lu : ~/%s"\n' "$f" > /tmp/bacasable/$f
done
HOME=/tmp/bacasable bash -lc true </dev/null
rm /tmp/bacasable/.bash_profile
HOME=/tmp/bacasable bash -lc true </dev/null
rm /tmp/bacasable/.bash_login
HOME=/tmp/bacasable bash -lc true </dev/null
```

```text
  lu : ~/.bash_profile
  lu : ~/.bash_login
  lu : ~/.profile
```

Cette astuce du `HOME` détourné est la meilleure façon d'expérimenter sur des
fichiers de profil : vous ne touchez jamais aux vôtres.

C'est aussi l'explication d'un grand classique. Le fichier réellement utilisé
dépend de ceux que la distribution a livrés dans votre `$HOME`, pas d'une règle
gravée : sur la machine de démonstration, `~/.bash_profile` est présent et
`~/.profile` absent, donc c'est le premier qui sert. Ailleurs, ce peut être
l'inverse. Ne le supposez pas, constatez-le :

```bash
ls -la ~/.bash_profile ~/.bash_login ~/.profile
```

Écrire dans un fichier que Bash n'atteint jamais ne produit aucune erreur : il
ne se passe simplement rien, ce qui est bien plus long à diagnostiquer.

### Où placer un `export` permanent

La question n'est pas de style : elle décide de qui verra la variable. Posons
un `export` dans chacun des deux fichiers :

```bash
echo 'export DEMO_DEPUIS_BASHRC=oui'  >> ~/.bashrc
echo 'export DEMO_DEPUIS_PROFILE=oui' >> ~/.bash_profile
```

Depuis une commande distante, c'est-à-dire sans login ni interaction :

```text
  DEMO_DEPUIS_BASHRC  = [oui]
  DEMO_DEPUIS_PROFILE = []
```

Depuis une session interactive ouverte au clavier :

```text
  DEMO_DEPUIS_BASHRC  = [oui]
  DEMO_DEPUIS_PROFILE = [oui]
```

Une variable posée dans `~/.bash_profile` seul est donc **invisible aux
commandes lancées à distance**, alors qu'elle apparaît dès qu'on se connecte
pour de bon. C'est la cause la plus fréquente d'un script qui marche au clavier
et échoue dans un `cron` ou dans un outil d'automatisation. Sur cette machine,
`~/.bashrc` est le seul emplacement vu dans les deux cas.

### Ne pas se verrouiller dehors

Un fichier de profil cassé se paie cher, parce qu'il est relu à chaque
connexion. Deux dégâts, très différents.

Une **erreur de syntaxe** est bruyante mais bénigne. Le shell signale la ligne,
abandonne la suite du fichier, et poursuit :

```bash
printf 'echo "ligne 1"\nexport X="guillemet non ferme\necho "ligne 3"\n' > /tmp/bacasable/.bash_profile
HOME=/tmp/bacasable bash -lc "echo CORPS-DE-LA-COMMANDE" </dev/null
echo "  code retour : $?"
```

```text
ligne 1
/tmp/bacasable/.bash_profile: line 3: unexpected EOF while looking for matching `"'
CORPS-DE-LA-COMMANDE
  code retour : 0
```

`ligne 1` s'affiche, `ligne 3` non : tout ce qui suit l'erreur est perdu. Mais
la commande demandée, elle, s'exécute bien.

Un `exit` égaré, lui, est silencieux et total. Le corps de la commande n'est
jamais exécuté, et le code retour reste `0` :

```bash
printf 'echo "debut du fichier"\nexit\necho "apres exit"\n' > /tmp/bacasable/.bash_profile
HOME=/tmp/bacasable bash -lc "echo CORPS-DE-LA-COMMANDE" </dev/null
echo "  code retour : $?"
```

```text
debut du fichier
  code retour : 0
```

`CORPS-DE-LA-COMMANDE` n'apparaît nulle part. Le même `exit` ajouté à un vrai
`~/.bashrc` rend la machine muette à toute commande distante : `ssh` se
connecte, n'exécute rien, et rend la main avec un succès apparent. Même `scp`
et `sftp` tombent, avec un message qui pointe le vrai coupable :

```text
Received message too long 1296126545
Ensure the remote shell produces no output for non-interactive sessions.
```

Ce message dit deux choses : un fichier de profil ne doit jamais rien afficher
en session non interactive, et c'est aussi pourquoi un simple `echo` de
bienvenue dans `~/.bashrc` casse les transferts de fichiers.

Quatre réflexes suffisent à travailler sans risque :

```bash
cp -a ~/.bashrc ~/.bashrc.bak          # 1. sauvegarder avant d'ecrire
bash -n ~/.bashrc                      # 2. controler la syntaxe sans executer
HOME=/tmp/bacasable bash -lc true      # 3. essayer dans un HOME jetable
bash -l                                # 4. essayer pour de vrai, en sous-shell
```

`bash -n` lit le fichier et signale les erreurs de syntaxe sans en exécuter une
seule ligne. Sur un fichier abîmé :

```text
/home/ansible/.bashrc: line 28: unexpected EOF while looking for matching `"'
```

Le quatrième réflexe est le plus important : `bash -l` ouvre un shell de login
**depuis la session déjà ouverte**. Si le résultat est catastrophique, vous
tapez `exit` et vous revenez dans une session saine, d'où vous restaurez la
sauvegarde. Ne fermez jamais votre dernière connexion avant d'avoir vérifié
qu'une nouvelle s'ouvre.

Et si le pire arrive quand même, l'issue de secours est un **second compte**
sur la machine : ses fichiers de profil à lui sont intacts, et s'il est dans
`wheel` il répare ceux du premier.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `bash: commande: command not found`, code retour `127` | le répertoire de la commande n'est pas dans `PATH` |
| Le programme enfant ne voit pas la variable | `export` oublié : `NOM=valeur` reste locale au shell |
| `NOM = valeur` répond `command not found` | des espaces autour du `=` |
| La variable disparaît après avoir lancé le fichier | le fichier a été exécuté au lieu d'être sourcé |
| La variable est là au clavier, absente en commande distante | l'`export` est dans `~/.bash_profile`, que les commandes distantes ne lisent pas |
| Rien ne change alors que `~/.profile` a été modifié | `~/.bash_profile` existe et gagne : les suivants ne sont pas lus |
| Un `echo` posé dans `/etc/profile.d/` ne s'affiche pas | `/etc/profile` jette leur sortie quand le shell n'est pas interactif ; sonder avec une variable, pas avec un `echo` |
| C'est le mauvais binaire qui s'exécute | le répertoire attendu est en fin de `PATH` au lieu du début |
| Plus aucune commande ne fonctionne dans le terminal | `$PATH` a été écrasé sans être réinjecté à la fin |
| `ssh` se connecte, ne fait rien, et renvoie `0` | un `exit` traîne dans un fichier de profil |
| `scp`/`sftp` : `Received message too long` | un fichier de profil affiche quelque chose en session non interactive |

Pour tout défaire et repartir de zéro :

```bash
rm -rf ~/demo-env /tmp/bacasable
sudo rm -f /etc/profile.d/00-trace.sh
cp -a ~/.bashrc.bak ~/.bashrc          # si vous aviez modifie ~/.bashrc
exec bash -l                           # recharger un shell propre
```

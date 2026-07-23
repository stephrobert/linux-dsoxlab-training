# Lab — premiers pas dans le terminal

## Rappel

[**Ouvrir un terminal et comprendre le prompt**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/prompt-terminal/)

Avant même que vous ayez tapé une seule lettre, le terminal affiche déjà une
ligne : l'**invite**, ou *prompt*. Le guide en donne la lecture : elle dit qui
vous êtes, sur quelle machine et dans quel répertoire vous vous trouvez, et son
dernier caractère annonce si vous travaillez en utilisateur ordinaire (`$`) ou
en administrateur (`#`). Il rappelle aussi trois mots que l'on confond
volontiers : le **terminal** est la fenêtre qui affiche du texte, le **shell**
est le programme qui interprète ce que vous tapez, la **session** est la
connexion active, du login au logout. Ce lab ajoute ce que la lecture seule ne
dit pas : d'où vient cette ligne (la variable `PS1`), comment savoir quel shell
tourne réellement, et quels gestes de saisie font gagner du temps dès la
première heure.

La structure d'une commande et l'interrogation de la documentation sont traitées
dans les labs voisins `l1-read-a-command` et `l1-get-help` : rien de tout cela
n'est repris ici.

## Le cours

Les exemples ci-dessous ne portent pas sur le challenge : ils travaillent dans
`/tmp/cours-l1-terminal`, un décor que vous fabriquez et que vous jetterez à la
fin. Le but est d'apprendre à lire son écran et à se servir de son clavier, pas
de recopier une réponse.

Toutes les sorties reproduites ici ont été relevées sur **Ubuntu 24.04.2 LTS**
avec `GNU bash, version 5.2.21(1)-release`, **sans un seul `sudo`**. La session
qui a servi aux captures tourne sous **zsh**, pas sous bash : chaque fois qu'un
comportement de bash est montré, bash a été lancé explicitement, avec
`bash -c '...'` pour une commande isolée et `script -qec "bash --norc -i"` quand
il fallait un vrai terminal interactif.

### L'invite, morceau par morceau

Plantez le décor, puis ouvrez un bash **sans configuration** grâce à `--norc` :

```bash
mkdir -p /tmp/cours-l1-terminal/atelier/notes/2026
cd /tmp/cours-l1-terminal
bash --norc -i
```

L'invite devient aussitôt `bash-5.2$` : c'est l'invite **par défaut de bash**,
compilée dans le programme et utilisée quand aucun fichier de configuration
n'est lu. Ni votre nom, ni la machine, ni le répertoire : tout cela vient de la
distribution, pas de bash. Vous quitterez ce shell avec `exit`. L'invite
habituelle d'une distribution ressemble plutôt à ceci (l'exemple du guide) :

```text
student@serveur:~$
```

| Élément | Signification |
|---|---|
| `student` | nom de l'utilisateur connecté |
| `@` et `:` | séparateurs |
| `serveur` | nom de la machine |
| `~` | répertoire courant (`~` est le raccourci du répertoire personnel) |
| `$` | vous êtes un utilisateur ordinaire (`#` si vous êtes root) |

Sur la machine de capture, après le `cd` du décor, l'invite réelle était
`student@poste:/tmp/cours-l1-terminal$`. Le répertoire n'y est plus `~` mais le
chemin du décor : cette partie **suit vos déplacements**, recalculée avant
chaque affichage. C'est la première raison de la lire.

### `$` ou `#` : la distinction qui coûte cher

Le guide est catégorique : si l'invite se termine par `#`, vous êtes **root**,
l'administrateur, et une erreur peut casser le système. Restez en utilisateur
ordinaire sauf besoin explicite.

Ce caractère n'est pas choisi au hasard dans la configuration : bash le décide
lui-même selon l'identité effective du processus. La séquence qui le produit est
`\$` ; sur un compte ordinaire elle donne `$`, avec un identifiant effectif égal
à 0 elle donne `#`. Les deux cas côte à côte (`${PS1@P}` demande à bash de
développer une invite comme il le ferait à l'écran, ce qui évite d'ouvrir une
vraie session) :

```bash
bash -c 'PS1='\''\u@\h:\w\$ '\''; echo "[${PS1@P}]"'
fakeroot -- bash -c 'PS1='\''\u@\h:\w\$ '\''; echo "[${PS1@P}]"'
```

```text
[student@poste:/tmp/cours-l1-terminal$ ]
[root@poste:/tmp/cours-l1-terminal# ]
```

> `fakeroot` n'est **pas** un moyen de devenir administrateur : il fait
> seulement croire aux programmes qu'ils tournent en root, sans leur en donner
> les droits. Il ne sert ici qu'à montrer le `#`. Sur une vraie session
> d'administration (`sudo -i`), ce `#` apparaît pour de bon.

Le réflexe à prendre : **avant de valider une commande destructrice, regardez le
dernier caractère de votre invite.**

### `PS1` : la recette derrière l'affichage

Tout ce qui précède tient dans une variable, `PS1`, et `echo "$PS1"` en révèle
la recette. Dans le bash sans configuration lancé plus haut, elle répond
`\s-\v\$ `, ce qui explique le `bash-5.2$` observé : `\s` est le nom du shell,
`\v` sa version, `\$` le caractère final. Dans un bash qui lit la configuration
de la distribution (`bash -i`), la même commande donne autre chose :

```text
${debian_chroot:+($debian_chroot)}\u@\h:\w\$
```

On y retrouve exactement l'invite `student@poste:/tmp/cours-l1-terminal$`. Cette
recette n'est pas tombée du ciel : sur cette machine Ubuntu, elle est écrite en
clair dans le fichier de configuration modèle des nouveaux comptes.

```bash
grep -n 'PS1=' /etc/skel/.bashrc
```

```text
60:    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
62:    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
[...]
```

Deux versions, choisies selon que le terminal sait afficher des couleurs ou non :
la ligne 62 est la version sobre, la ligne 60 la même avec des codes de couleur
(`\[\033[01;32m\]` et compagnie) intercalés.

| Séquence | Ce qu'elle affiche |
|---|---|
| `\u` | nom de l'utilisateur |
| `\h` | nom de la machine |
| `\w` | répertoire courant, chemin complet (`~` pour le répertoire personnel) |
| `\W` | répertoire courant, **dernier élément seulement** |
| `\$` | `#` si l'identifiant effectif est 0, `$` sinon |
| `\s` `\v` | nom et version du shell |

La différence entre `\w` et `\W` se voit en deux lignes, depuis
`/tmp/cours-l1-terminal/atelier/notes/2026` :

```bash
bash -c 'PS1='\''\u@\h:\w\$ '\''; echo "${PS1@P}"'
bash -c 'PS1='\''\u@\h:\W\$ '\''; echo "${PS1@P}"'
```

```text
student@poste:/tmp/cours-l1-terminal/atelier/notes/2026$
student@poste:2026$
```

`\W` tient dans un coin d'écran mais ne dit pas où vous êtes : deux répertoires
`2026` situés dans deux arborescences différentes s'y affichent à l'identique.

### Terminal, shell, console : trois choses distinctes

La confusion la plus tenace du débutant se dissipe avec deux commandes qui **ne
répondent pas la même chose**. Lancées d'abord dans la session de capture, puis
à l'intérieur d'un bash :

```bash
echo "$SHELL" ; ps -p $$ -o comm=
bash -c 'echo "$SHELL" ; ps -p $$ -o comm='
```

```text
/usr/bin/zsh
zsh
/usr/bin/zsh
bash
```

`$SHELL` n'a pas bougé, et c'est normal : cette variable contient le shell
**déclaré pour votre compte** dans la base des utilisateurs, pas celui qui
tourne. Ce champ se lit directement, c'est le septième de la ligne :
`getent passwd "$(id -u)" | cut -d: -f7` répond ici `/usr/bin/zsh`, la même
valeur que `$SHELL`.

`ps -p $$ -o comm=`, lui, interroge le processus courant : `$$` est le numéro du
shell en cours et `comm` son nom. C'est **la** réponse fiable à la question
« dans quel shell suis-je ? ». Les deux divergent dès qu'un shell en lance un
autre, ce qui arrive tout le temps.

Le terminal, lui, est un **autre processus**, parent du shell :

```bash
ps -o pid,tty,comm --forest -p $PPID --ppid $PPID
```

```text
    PID TT       COMMAND
1768434 ?        script
1768437 pts/9     \_ bash
```

La fenêtre (ici `script`, le programme qui a fourni le terminal pour la capture ;
sur un bureau ce serait `gnome-terminal` ou `konsole`) et le shell qu'elle
héberge sont bien deux processus séparés. Fermez la fenêtre, le shell meurt ;
tapez `exit` dans le shell, la fenêtre se ferme. Ils restent distincts.

Le lien entre les deux porte un nom de fichier, que `tty` affiche :
`/dev/pts/9`. `pts` veut dire *pseudo-terminal*, un terminal émulé par un
programme. La **console**, elle, est le terminal physique de la machine, celui
que vous voyez sur l'écran branché au serveur avant même qu'un bureau graphique
démarre ; elle existe indépendamment de toute fenêtre et porte un autre nom, que
`ls -l /dev/tty1` montre bien présent :
`crw--w---- 1 root tty 4, 1 juil. 14 07:50 /dev/tty1`.

Reste la variable `TERM`, qui dit **de quel modèle de terminal** il s'agit. Elle
sert aux programmes qui dessinent à l'écran (couleurs, position du curseur) pour
savoir ce qu'ils ont le droit d'envoyer :

```bash
echo "$TERM" ; tput colors
```

```text
xterm-256color
256
```

> La session de capture n'ayant pas de `TERM`, la valeur a été fixée
> explicitement sur la ligne de commande pour cette démonstration. Dans un vrai
> terminal, c'est le terminal lui-même qui la renseigne. Un `TERM` absent ou
> incorrect donne un affichage sans couleur, voire des caractères parasites.

### Les gestes qui font gagner du temps

**La touche Tab complète.** Tapez le début d'une commande ou d'un chemin puis
Tab : le shell termine le mot s'il n'y a qu'une possibilité. S'il y en a
plusieurs, une **deuxième** frappe de Tab les liste toutes. La commande
`compgen` montre ce que Tab proposerait, sans avoir à appuyer dessus :

```bash
compgen -f /etc/os-
compgen -c sys | sort -u | head -5
```

```text
/etc/os-release
syscount-bpfcc
syscount.bt
sysctl
syslinux
systemctl
```

Un seul candidat pour `/etc/os-`, donc Tab complète directement ; plusieurs pour
`sys`, donc Tab-Tab affiche la liste. Complétez systématiquement : c'est plus
rapide, et une faute de frappe dans un chemin devient impossible.

**L'historique évite de retaper.** Le shell garde ce que vous avez tapé. La
flèche Haut remonte commande par commande, `history` affiche la liste numérotée
et `!<numéro>` rejoue une ligne :

```text
bash-5.2$ history
    1  cd /tmp/cours-l1-terminal
    2  ls atelier
    3  pwd
    4  history
bash-5.2$ !2
ls atelier
notes
```

`!2` **réaffiche** la commande avant de l'exécuter : vous voyez ce que vous
relancez. Pour retrouver une ligne sans connaître son numéro, **Ctrl+R** ouvre
une recherche dans l'historique ; tapez quelques lettres, la correspondance la
plus récente s'affiche, Entrée l'exécute. Après la frappe de `atel`, la ligne
affichée était :

```text
(reverse-i-search)`atel': ls atelier/notes
```

**Les raccourcis d'édition évitent la flèche Gauche.** Ils se répartissent en
deux familles, et la distinction est utile : certains sont gérés par le
**terminal** lui-même (ils fonctionnent même quand aucun shell n'écoute), les
autres par la bibliothèque d'édition de bash.

| Raccourci | Effet | Géré par |
|---|---|---|
| **Ctrl+A** | aller au début de la ligne | bash |
| **Ctrl+E** | aller à la fin de la ligne | bash |
| **Ctrl+U** | effacer du curseur jusqu'au début | terminal et bash |
| **Ctrl+W** | effacer le mot avant le curseur | terminal et bash |
| **Ctrl+L** | effacer l'écran | bash |
| **Ctrl+R** | rechercher dans l'historique | bash |
| **Ctrl+C** | interrompre la commande en cours | terminal |
| **Ctrl+D** | fin de saisie ; sur une ligne vide, ferme le shell | terminal |

Ce tableau n'est pas une opinion. Côté bash, `bind -P` liste les associations
réellement en place ; voici les lignes qui nous concernent :

```text
beginning-of-line can be found on "\C-a", "\eOH", "\e[1~", "\e[H".
clear-screen can be found on "\C-l".
complete can be found on "\C-i", "\e\e\000".
end-of-line can be found on "\C-e", "\eOF", "\e[4~", "\e[F".
possible-completions can be found on "\e=", "\e?".
reverse-search-history can be found on "\C-r".
unix-line-discard can be found on "\C-u".
unix-word-rubout can be found on "\C-w".
```

`\C-a` se lit « Ctrl+A », et `\C-i` est le code de la touche Tab : la complétion
est donc un raccourci comme les autres. Côté terminal, `stty -a` montre les
caractères de contrôle interceptés avant même que le shell les voie :

```text
intr = ^C; quit = ^\; erase = ^?; kill = ^U; eof = ^D; eol = <undef>;
[...]
werase = ^W; lnext = ^V; discard = ^O; min = 1; time = 0;
```

`intr = ^C` signifie que le terminal transforme ce caractère en signal
d'interruption : c'est pourquoi **Ctrl+C** fonctionne même sur un programme qui
ne connaît rien de bash. Vérification, avec une commande qui dure :

```text
bash-5.2$ sleep 30
^C
bash-5.2$ echo "code retour = $?"
code retour = 130
```

Le `130` est la signature d'une commande tuée par Ctrl+C. Enfin, **Ctrl+D** sur
une ligne **vide** ferme la session : c'est l'équivalent clavier de `exit`.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| l'invite affiche `#` | vous êtes root, ou dans un `sudo -i` | `id -u` ; s'il répond `0`, sortez avec `exit` |
| l'invite se réduit à `bash-5.2$` | le shell ne lit pas la configuration du compte | relancer sans `--norc`, ou vérifier `~/.bashrc` |
| `echo "$SHELL"` ne correspond pas au shell utilisé | `$SHELL` donne le shell déclaré, pas celui qui tourne | `ps -p $$ -o comm=` |
| Tab ne complète rien | aucun candidat, ou complétion non installée | `compgen -c <début>` pour voir les candidats |
| `\$` dans `PS1` affiche toujours `$` | `PS1` a été défini entre guillemets **doubles**, où `\$` devient un `$` littéral | redéfinir `PS1` entre guillemets **simples** |
| affichage sans couleur, ou caractères parasites | `TERM` absent ou incorrect | `echo "$TERM"` puis `tput colors` |
| les raccourcis Ctrl+quelque chose ne répondent pas | vous n'êtes pas dans une saisie interactive du shell | `tty` doit répondre un `/dev/pts/...` |
| Ctrl+D ne ferme pas le shell | la variable `IGNOREEOF` est définie | utiliser `exit` |

Pour finir, quittez le bash jetable et effacez le décor :

```bash
exit
rm -rf /tmp/cours-l1-terminal
```

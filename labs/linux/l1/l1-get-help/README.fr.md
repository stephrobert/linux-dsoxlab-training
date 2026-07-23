# Lab — obtenir de l'aide en ligne de commande

## Rappel

[**Obtenir de l'aide sous Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/obtenir-aide/)

Personne ne retient toutes les options de toutes les commandes, et ce n'est pas
la compétence attendue : un système Linux embarque sa propre documentation, et
ce qu'on vous demande c'est de savoir laquelle interroger. `<commande> --help`
donne un rappel rapide, `man` est la référence, `info` héberge les manuels GNU
détaillés, `apropos` et `whatis` retrouvent un nom quand vous ne le connaissez
pas. Le manuel lui-même est découpé en **sections numérotées** : un même nom
peut y figurer plusieurs fois sans désigner la même chose.

## Le cours

Les exemples ci-dessous portent sur `passwd`, `printf`, `ls`, `cp` et `echo` :
le challenge, lui, vous demandera d'autres commandes, qu'il faudra justement
trouver avec les outils présentés ici. Le but est d'apprendre à interroger la
documentation d'un système, pas de recopier une ligne.

Toutes les sorties reproduites ici ont été relevées sur **Debian 12
(bookworm)**, avec `man 2.11.2`, `GNU bash 5.2.15` et `info (GNU texinfo) 6.8`.
Les deux relevés faits ailleurs sont signalés comme tels.

Premier réflexe avant tout le reste : vérifier de quoi vous disposez, car sur
une installation minimale ces outils sont absents. Relevé sur une image
**AlmaLinux 10** minimale, `command -v man info apropos` n'affiche aucune ligne
et sort avec le code retour 1 : les trois commandes manquent, et le guide donne
les paquets à poser selon la distribution.

### Trois sources, et elles ne disent pas la même chose

Prenez `ls`, et comparez ce que chacune des trois sources produit :

| Source | Commande | Volume mesuré |
|---|---|---|
| Aide intégrée au binaire | `ls --help` | 138 lignes |
| Page de manuel | `man ls` | 252 lignes |
| Manuel GNU | `info '(coreutils) ls invocation'` | 832 lignes |

Ce n'est pas le même texte gonflé trois fois : la page man renvoie elle-même
vers `info` dans son `SEE ALSO`, par la ligne
`or available locally via: info '(coreutils) ls invocation'`. Le manuel `info`
contient des chapitres entiers que la page man n'a pas (`Sorting the output`,
`Formatting file timestamps`, la variable `LS_COLORS`). Pour les outils GNU
(coreutils, `find`, `sed`, `awk`), c'est là qu'est le texte le plus complet.

Le cas où `--help` et `man` divergent vraiment, lui, est plus vicieux. Dans
bash, `echo` existe **en double** : une commande interne au shell, et un
programme `/usr/bin/echo`. Le shell donne toujours la priorité à la sienne.

```bash
echo --help
type -a echo
```

```text
--help
echo is a shell builtin
echo is /usr/bin/echo
echo is /bin/echo
```

`echo --help` n'affiche pas d'aide : il **affiche le texte `--help`**, parce que
la version interne ne connaît pas cette option et la traite comme une chaîne à
afficher. Le programme, lui, la comprend (`/usr/bin/echo --help` répond
`Usage: /usr/bin/echo [SHORT-OPTION]... [STRING]...`), et c'est bien ce
programme-là, celui que vous n'exécutez pas, que documente `man echo`.

> **La leçon.** Avant de croire une page de manuel, vérifiez que c'est bien ce
> programme-là que le shell lance. C'est le rôle de `type`, dernière section.

### Le manuel est découpé en sections numérotées

C'est le point que presque personne ne connaît, et celui qui sépare quelqu'un
qui cherche de quelqu'un qui trouve. `man 1 man` en donne la liste :

```text
1   Executable programs or shell commands
2   System calls (functions provided by the kernel)
3   Library calls (functions within program libraries)
4   Special files (usually found in /dev)
5   File formats and conventions, e.g. /etc/passwd
[...]
8   System administration commands (usually only for root)
9   Kernel routines [Non standard]
```

Le numéro se place **avant** le nom. Voyez ce que cela change sur `passwd` :

```bash
man 1 passwd
man 5 passwd
```

```text
PASSWD(1)                      User Commands                     PASSWD(1)

NAME
       passwd - change user password

SYNOPSIS
       passwd [options] [LOGIN]
[...]
PASSWD(5)             File Formats and Configuration             PASSWD(5)

NAME
       passwd - the password file

DESCRIPTION
       /etc/passwd contains one line for each user account, with seven
       fields delimited by colons (":"). These fields are:
[...]
```

Deux documentations sans rapport : la **commande** qui change un mot de passe
d'un côté, le **format du fichier** `/etc/passwd` de l'autre. Même chose pour
`printf`, utilitaire en section 1 et fonction du langage C en section 3 :

```bash
man 3 printf
```

```text
printf(3)                Library Functions Manual                printf(3)

NAME
       printf, fprintf, dprintf, sprintf, snprintf, vprintf, vfprintf, vd-
       printf, vsprintf, vsnprintf - formatted output conversion
[...]
```

Sans numéro, `man` ouvre la **première section trouvée**, dans l'ordre des
numéros : `man printf` vous donne donc la section 1, et vous ne saurez jamais
que la 3 existe si vous ne la demandez pas.

### Savoir qu'un nom existe dans plusieurs sections

`whatis` (identique à `man -f`) liste toutes les sections où un nom apparaît,
avec sa description en une ligne :

```bash
whatis printf
man -f man
```

```text
printf (1)           - format and print data
printf (3)           - formatted output conversion
man (1)              - an interface to the system reference manuals
man (7)              - macros to format man pages
```

C'est le réflexe à prendre avant d'ouvrir une page : en une ligne, vous savez
combien de documentations différentes portent ce nom. `man -a printf` les
enchaîne ensuite toutes, en vous proposant de passer à la suivante à la fin de
chacune.

Pour savoir d'où sortent ces pages, `man -w` affiche le chemin du fichier au
lieu de son contenu, et `-aw` les affiche tous : `man -aw passwd` répond
`/usr/share/man/man1/passwd.1.gz` puis `/usr/share/man/man5/passwd.5.gz`.

### Chercher quand on ne connaît pas le nom

`apropos` (identique à `man -k`) cherche votre motif dans les descriptions en
une ligne de **toutes** les pages installées. L'option `-s` restreint à une
section, ce qui évite de noyer une recherche de fichier de configuration sous
les commandes :

```bash
apropos "copy files"
apropos -s 5 password
```

```text
cp (1)               - copy files and directories
install (1)          - copy files and set attributes
login.defs (5)       - shadow password suite configuration
passwd (5)           - the password file
shadow (5)           - shadowed password file
```

Attention : `apropos` compare votre motif au **texte exact** de la description.
Il ne comprend pas les synonymes, et une formulation naturelle échoue souvent :

```bash
apropos "disk usage"
echo "code retour = $?"
apropos "space usage"
```

```text
disk usage: nothing appropriate.
code retour = 16
df (1)               - report file system space usage
du (1)               - estimate file space usage
```

Les deux commandes existent pourtant, mais leur description dit `space usage`,
pas `disk usage`. Le remède est `-a`, qui accepte plusieurs mots-clés dans
n'importe quel ordre : `apropos -a file space usage` retrouve bien `df` et `du`.

**Le piège suivant est plus grave.** `apropos` et `whatis` ne lisent pas les
pages : ils interrogent une **base d'index** construite par `mandb`. Si cet
index manque ou date, ils répondent `nothing appropriate` alors que la page
existe. Démonstration, index mis de côté :

```bash
apropos "copy files"
echo "code retour = $?"
man cp
```

```text
copy files: nothing appropriate.
code retour = 16
CP(1)                          User Commands                         CP(1)

NAME
       cp - copy files and directories
```

`apropos` échoue, `man cp` réussit et affiche cette description mot pour mot :
la page est là, c'est l'index qui manque. `mandb`, lancé en root, le reconstruit
(`3314 manual pages were added.`), après quoi `apropos "copy files"` retrouve
`cp` et `install` avec le code retour 0.

Le même message apparaît pour la raison inverse, et c'est le cas du poste sur
lequel ce lab a été préparé, une **Ubuntu 24.04 allégée** où `man-db` est
installé mais où presque toutes les pages ont été supprimées. L'index y est
parfaitement à jour, il n'indexe simplement que le peu qui reste :

```text
$ whatis psql
psql (1)             - PostgreSQL interactive terminal
$ whatis ls
ls: nothing appropriate.
```

Deux causes, un seul message. `man -w <nom>` tranche : s'il ne renvoie aucun
chemin, la page manque vraiment.

### Lire une page man sans la lire en entier

`man` vous dépose dans le pager `less` : **Espace** avance d'une page, **b**
recule, **/motif** cherche vers l'avant, **n** et **N** sautent à l'occurrence
suivante et précédente, **q** quitte.

Les pages suivent toujours le même plan, et c'est ce qui permet de sauter au bon
endroit : **NAME** (est-ce la bonne commande), **SYNOPSIS** (la syntaxe, avec
des crochets pour l'optionnel), **DESCRIPTION**, **OPTIONS** (la liste
complète), **EXAMPLES**, **FILES**, **SEE ALSO** (les commandes voisines),
**EXIT STATUS** (les codes de retour). Dans une page longue, tapez `/EXAMPLES`
puis Entrée pour y aller d'un coup.

### `which`, `type`, `command -v` : trois questions différentes

`which` cherche un **fichier** dans le `PATH`. `type` interroge le **shell**, et
connaît donc aussi les alias, les fonctions et les commandes internes. Sur `cd`,
interne à bash et sans fichier, les deux divergent franchement :

```bash
type cd
which cd
echo "code retour = $?"
command -v cd
```

```text
cd is a shell builtin
code retour = 1
cd
```

`which` ne renvoie rien et sort en erreur, alors que la commande existe et
fonctionne. Pire, il peut vous renvoyer un chemin qui n'est pas ce qui
s'exécute :

```bash
which pwd
type -a pwd
```

```text
/usr/bin/pwd
pwd is a shell builtin
pwd is /usr/bin/pwd
pwd is /bin/pwd
```

`type -a` liste toutes les possibilités **dans l'ordre de priorité** : c'est la
première, la version interne, qui sera lancée, alors que `which` désigne la
deuxième. Les alias et les fonctions échappent de la même manière à `which` :

```bash
alias ll='ls -l --human-readable'
type ll
which ll
echo "code retour = $?"
```

```text
ll is aliased to `ls -l --human-readable'
code retour = 1
```

`type -t` répond en un seul mot, ce qui est pratique dans un script : `alias`,
`function`, `builtin`, `file`, ou rien du tout.

Reste le cas des commandes internes : `man cd` échoue avec
`No manual entry for cd` (code retour 16), parce qu'elles ne sont pas
documentées par des pages séparées mais par le shell lui-même, via `help` :

```bash
help cd
```

```text
cd: cd [-L|[-P [-e]] [-@]] [dir]
    Change the shell working directory.

    Change the current directory to DIR.  The default DIR is the value of the
    HOME shell variable. If DIR is "-", it is converted to $OLDPWD.
[...]
```

`help -d cd` en donne la version d'une ligne, `help` seul liste toutes les
commandes internes. Elles figurent aussi dans `man bash`, section
`SHELL BUILTIN COMMANDS`, mais c'est une page de plusieurs milliers de lignes.

### Dépannage

| Symptôme | Cause probable | Vérification |
|---|---|---|
| `No manual entry for xxx` sur une commande qui marche | commande interne au shell | `type xxx`, puis `help xxx` |
| `No manual entry for xxx` sur un vrai programme | page non installée | `man -w xxx`, puis installer le paquet de doc |
| `nothing appropriate` mais `man` fonctionne | index `mandb` absent ou périmé | reconstruire l'index avec `mandb` |
| `nothing appropriate` et `man -w` ne renvoie rien | les pages elles-mêmes manquent | installer `man-pages` / `manpages` |
| `apropos: command not found` | `man-db` non installé | voir les paquets en tête du guide |
| `man` affiche la mauvaise documentation | mauvaise section retenue | `whatis nom`, puis `man <numéro> nom` |
| `<commande> --help` affiche `--help` | commande interne qui ignore l'option | `help commande` |
| la page man ne colle pas à ce qui s'exécute | un autre binaire est lancé | `type -a commande` |

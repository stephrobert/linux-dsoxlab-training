# Lab — répertoire collaboratif avec set-GID

## Rappel

[**Permissions & propriété sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/)

Sur un répertoire, le bit **set-GID** (`chmod g+s`, ou le `2` de tête d'un mode
octal à quatre chiffres) fait hériter les nouveaux fichiers du groupe du
répertoire. Combiné au bon groupe et à `g+w`, c'est un dossier collaboratif :
le guide en fait le complément naturel d'un UMASK bien réglé, parce que c'est
lui qui rend le travail à plusieurs sur un même groupe réellement fonctionnel.
`ls -ld` montre un `s` à la place de l'exécution du groupe.

## Le cours

Les exemples ci-dessous travaillent sur `/srv/chantier`, un répertoire de
démonstration, avec le groupe `redaction` et les comptes `nadia` et `pierre` :
le challenge, lui, vous demandera un autre chemin, un autre groupe et d'autres
comptes. Le but est d'apprendre la méthode, pas de recopier une ligne.

### Le décor de démonstration

```bash
sudo groupadd redaction
sudo useradd -m -G redaction nadia
sudo useradd -m -G redaction pierre
sudo mkdir -p /srv/chantier
sudo chown root:root /srv/chantier
sudo chmod 0755 /srv/chantier
```

Avant de toucher aux droits, regardez ce que vous avez :

```bash
ls -ld /srv/chantier
stat -c '%n %a %U:%G' /srv/chantier
id nadia
```

```text
drwxr-xr-x. 2 root root 6 Jul 22 12:20 /srv/chantier
/srv/chantier 755 root:root
uid=1005(nadia) gid=1008(nadia) groups=1008(nadia),1007(redaction)
```

Deux choses à lire dans le `id` : `nadia` a un **groupe primaire** à son nom
(`gid=1008(nadia)`), et `redaction` n'est qu'un groupe **secondaire**. C'est de
là que vient tout le problème qui suit.

Le point final de `drwxr-xr-x.` n'a rien à voir avec les droits : il signale un
contexte SELinux, actif sur cette VM (`getenforce` répond `Enforcing`).

### Le problème : chaque fichier garde le groupe de son auteur

Donnons déjà le bon groupe au répertoire et l'écriture au groupe, mais **sans**
le bit set-GID :

```bash
sudo chgrp redaction /srv/chantier
sudo chmod 0770 /srv/chantier
ls -ld /srv/chantier
```

```text
drwxrwx---. 2 root redaction 6 Jul 22 12:20 /srv/chantier
```

Le répertoire est au bon groupe, les deux comptes peuvent y écrire. Pourtant la
collaboration ne marche pas :

```bash
sudo -u nadia touch /srv/chantier/plan.md
sudo ls -l /srv/chantier/plan.md
```

```text
-rw-r--r--. 1 nadia nadia 0 Jul 22 12:20 /srv/chantier/plan.md
```

Le fichier est né avec le groupe **`nadia`**, pas `redaction` : par défaut, un
nouveau fichier prend le **groupe primaire de son créateur**. La conséquence est
immédiate :

```bash
sudo -u pierre sh -c 'echo revision >> /srv/chantier/plan.md'
```

```text
sh: line 1: /srv/chantier/plan.md: Permission denied
```

`pierre` est pourtant membre de `redaction`, mais le fichier n'appartient pas à
`redaction`. Un dossier partagé où personne ne peut reprendre le travail de
l'autre n'est pas un dossier collaboratif.

Notez au passage que sur un répertoire en `0770`, votre propre compte
d'administration n'est pas membre du groupe : un simple `ls -l /srv/chantier`
échoue en `Permission denied`. C'est `sudo ls -l` qu'il faut taper, sinon on
croit à tort que le répertoire est cassé.

### Poser le bit set-GID

```bash
sudo chmod g+s /srv/chantier
sudo ls -ld /srv/chantier
sudo stat -c '%a' /srv/chantier
```

```text
drwxrws---. 2 root redaction 21 Jul 22 12:20 /srv/chantier
2770
```

Le `x` du groupe est devenu un **`s`**, et le mode octal a gagné un chiffre de
tête : `770` est devenu `2770`. Les deux écritures sont équivalentes :

```bash
sudo chmod g+s /srv/chantier      # symbolique
sudo chmod 2770 /srv/chantier     # octal, le 2 de tête est le set-GID
```

Le nouveau fichier hérite alors du groupe du répertoire :

```bash
sudo -u nadia touch /srv/chantier/note.md
sudo ls -l /srv/chantier
```

```text
-rw-r--r--. 1 nadia redaction 0 Jul 22 12:20 note.md
-rw-r--r--. 1 nadia nadia     0 Jul 22 12:20 plan.md
```

`note.md`, créé après la pose du bit, est au groupe `redaction`. `plan.md`,
créé avant, n'a pas bougé : nous y reviendrons.

### Le `s` minuscule, et le `S` majuscule qui trahit une erreur

Le bit set-GID s'affiche à la place du `x` du groupe. Si ce `x` n'existe pas,
`ls` le signale par une **majuscule** :

```bash
sudo chmod g-x /srv/chantier
sudo stat -c '%a %A' /srv/chantier
```

```text
2760 drwxrwS---
```

Le bit est bien posé (le `2` est là), mais le groupe ne peut plus **traverser**
le répertoire : personne n'y entrera, donc l'héritage ne servira jamais. Un `S`
majuscule est presque toujours le signe d'un `g+x` oublié.

```bash
sudo chmod g+x /srv/chantier
sudo stat -c '%a %A' /srv/chantier
```

```text
2770 drwxrws---
```

### Le piège de `chmod` en numérique

Sur un **répertoire**, `chmod` ne retire pas le set-GID quand on lui donne un
mode numérique ordinaire, même à quatre chiffres :

```bash
sudo chmod g+s /srv/chantier  ; sudo stat -c '%a %A' /srv/chantier
sudo chmod 755 /srv/chantier  ; sudo stat -c '%a %A' /srv/chantier
sudo chmod 0755 /srv/chantier ; sudo stat -c '%a %A' /srv/chantier
```

```text
2755 drwxr-sr-x
2755 drwxr-sr-x
2755 drwxr-sr-x
```

Le bit survit aux deux « remises à plat ». Ce n'est pas un accident, c'est
documenté dans `man chmod`, section *SETUID AND SETGID BITS* :

> For directories chmod preserves set-user-ID and set-group-ID bits unless you
> explicitly specify otherwise. You can set or clear the bits with symbolic
> modes like u+s and g-s. To clear these bits for directories with a numeric
> mode requires an additional leading zero like 00755, leading minus like
> -6000, or leading equals like =755.

Les trois formes annoncées fonctionnent bien, vérification faite :

```bash
sudo chmod g-s /srv/chantier   ; sudo stat -c '%a %A' /srv/chantier   # 755 drwxr-xr-x
sudo chmod 00755 /srv/chantier ; sudo stat -c '%a %A' /srv/chantier   # 755 drwxr-xr-x
sudo chmod =755 /srv/chantier  ; sudo stat -c '%a %A' /srv/chantier   # 755 drwxr-xr-x
```

Retenez le réflexe **`g-s`** pour retirer un set-GID. Et si un audit signale un
répertoire encore set-GID après un `chmod` numérique, ce n'est pas l'audit qui
se trompe.

### Hériter du groupe ne suffit pas : l'UMASK

Remettons le répertoire en `2770` et regardons le fichier hérité de tout à
l'heure. Il est au groupe `redaction`, et pourtant :

```bash
sudo -u pierre sh -c 'echo revision >> /srv/chantier/note.md'
```

```text
sh: line 1: /srv/chantier/note.md: Permission denied
```

La raison est dans le mode du fichier, `-rw-r--r--` : le groupe le **lit** mais
ne l'**écrit** pas. Le set-GID donne le bon groupe, il ne donne aucun droit. Les
droits d'un nouveau fichier, eux, viennent de l'**UMASK** de son créateur, dont
le guide rappelle qu'il « définit les permissions retirées aux nouveaux
fichiers » et vaut **022** par défaut :

```bash
sudo -u nadia sh -c 'umask'
```

```text
0022
```

`022` retire l'écriture au groupe, d'où le `-rw-r--r--`. Avec un UMASK qui ne
retire rien au groupe, le fichier naît utilisable à deux :

```bash
sudo -u nadia sh -c 'umask 007; touch /srv/chantier/agenda.md'
sudo ls -l /srv/chantier/agenda.md
sudo -u pierre sh -c 'echo revision >> /srv/chantier/agenda.md'
sudo ls -l /srv/chantier/agenda.md
```

```text
-rw-rw----. 1 nadia redaction 0 Jul 22 12:20 /srv/chantier/agenda.md
-rw-rw----. 1 nadia redaction 9 Jul 22 12:20 /srv/chantier/agenda.md
```

Cette fois `pierre` écrit : le fichier a grossi. `007` retire tout aux
« autres » et ne retire rien au groupe. `002` fait de même en laissant la
lecture à tous, ce qui se voit sur le mode obtenu :

```bash
sudo -u nadia sh -c 'umask 002; touch /srv/chantier/essai-002.md'
sudo ls -l /srv/chantier/essai-002.md
```

```text
-rw-rw-r--. 1 nadia redaction 0 Jul 22 12:23 /srv/chantier/essai-002.md
```

> **Attention à `027`, la valeur de durcissement recommandée par le guide.**
> Le guide la décrit comme « rien pour les autres, lecture pour le groupe », et
> c'est très exactement ce qu'elle fait :
>
> ```bash
> sudo -u nadia sh -c 'umask 027; touch /srv/chantier/essai-027.md'
> sudo ls -l /srv/chantier/essai-027.md
> sudo -u pierre sh -c 'echo x >> /srv/chantier/essai-027.md'
> ```
>
> ```text
> -rw-r-----. 1 nadia redaction 0 Jul 22 12:20 /srv/chantier/essai-027.md
> sh: line 1: /srv/chantier/essai-027.md: Permission denied
> ```
>
> Sous `027`, le groupe **lit** et ne modifie pas. Pour un répertoire où l'on
> co-édite, il faut `007` (ou `002`). Le durcissement global et le besoin d'un
> service se règlent donc à deux endroits différents, et non l'un contre
> l'autre.

Un `umask` tapé dans un shell disparaît avec lui. Le guide indique où le rendre
persistant : `/etc/login.defs` (utilisé par `useradd` et `pam_umask`) et un
fichier dédié dans `/etc/profile.d/` pour les shells interactifs. L'effet du
second se vérifie tout de suite, dans un shell de login :

```bash
sudo -u nadia bash -lc 'umask'                                    # 0022
echo 'umask 007' | sudo tee /etc/profile.d/99-chantier-demo.sh
sudo -u nadia bash -lc 'umask'                                    # 0007
sudo rm -f /etc/profile.d/99-chantier-demo.sh
sudo -u nadia bash -lc 'umask'                                    # 0022
```

Mesurez la portée du geste avant de le faire : un fichier déposé dans
`/etc/profile.d/` s'applique à **tous** les comptes qui ouvrent un shell de
login, pas aux seuls membres du groupe.

### Les sous-répertoires héritent aussi du bit

C'est ce qui rend le montage durable : le set-GID se propage de proche en
proche, sans qu'on repasse derrière chaque création.

```bash
sudo -u nadia sh -c 'umask 007; mkdir /srv/chantier/brouillons'
sudo stat -c '%n %a %A %U:%G' /srv/chantier/brouillons
```

```text
/srv/chantier/brouillons 2770 drwxrws--- nadia:redaction
```

Le sous-répertoire a hérité du groupe **et** du bit set-GID lui-même. Ce qui
sera créé dedans héritera à son tour.

### Rattraper ce qui existait déjà

L'héritage ne vaut que pour l'avenir. Les fichiers antérieurs gardent leur
groupe, et il faut aller les chercher :

```bash
sudo chgrp -R redaction /srv/chantier
sudo chmod -R g+w /srv/chantier
sudo ls -l /srv/chantier
```

```text
-rw-rw----. 1 nadia redaction 9 Jul 22 12:20 agenda.md
-rw-rw----. 1 nadia redaction 0 Jul 22 12:20 essai-027.md
-rw-rw-r--. 1 nadia redaction 0 Jul 22 12:20 note.md
-rw-rw-r--. 1 nadia redaction 0 Jul 22 12:20 plan.md
```

(extrait : seuls les fichiers ordinaires sont repris ici.)

Il faut bien les **deux** commandes : `chgrp -R` seul corrige le groupe et
laisse les fichiers en `-rw-r--r--`, donc toujours fermés en écriture pour le
groupe.

Et prenez le mode symbolique. Un `chmod -R 770` sur la même arborescence donne
ceci :

```bash
sudo chmod -R 770 /srv/chantier
sudo ls -l /srv/chantier
sudo stat -c '%n %a %A' /srv/chantier /srv/chantier/brouillons
```

```text
-rwxrwx---. 1 nadia redaction 9 Jul 22 12:20 agenda.md
drwxrws---. 2 nadia redaction 6 Jul 22 12:20 brouillons
-rwxrwx---. 1 nadia redaction 0 Jul 22 12:23 essai-002.md
...
/srv/chantier 2770 drwxrws---
/srv/chantier/brouillons 2770 drwxrws---
```

Tous les fichiers ordinaires sont devenus **exécutables**, ce que personne n'a
demandé, alors que le set-GID des répertoires, lui, a survécu comme on l'a vu
plus haut. La forme récursive numérique donne donc l'exact inverse de ce qu'on
attend d'elle.

### `cp` hérite, `mv` non

Le piège le plus coûteux en production : déplacer un fichier dans le répertoire
ne le fait **pas** passer au groupe.

```bash
sudo -u nadia sh -c 'umask 007; touch /home/nadia/source-a.md /home/nadia/source-b.md'
sudo -u nadia cp /home/nadia/source-a.md /srv/chantier/copie.md
sudo -u nadia mv /home/nadia/source-b.md /srv/chantier/deplace.md
sudo ls -l /srv/chantier/copie.md /srv/chantier/deplace.md
```

```text
-rw-r-----. 1 nadia redaction 0 Jul 22 12:21 /srv/chantier/copie.md
-rw-rw----. 1 nadia nadia     0 Jul 22 12:21 /srv/chantier/deplace.md
```

`cp` **crée** un fichier dans le répertoire : le set-GID s'applique, et l'UMASK
du moment aussi (d'où le `-rw-r-----`, l'UMASK valant `022` dans ce shell).
`mv` à l'intérieur d'un même système de fichiers ne crée rien, il renomme : le
fichier arrive avec son groupe d'origine, `nadia`, et personne d'autre ne
pourra le reprendre.

Même résultat avec `cp -p`, qui **préserve** explicitement la propriété :

```bash
sudo -u nadia sh -c 'umask 007; touch /home/nadia/source-c.md'
sudo -u nadia cp -p /home/nadia/source-c.md /srv/chantier/copie-p.md
sudo ls -l /srv/chantier/copie-p.md
```

```text
-rw-rw----. 1 nadia nadia 0 Jul 22 12:21 /srv/chantier/copie-p.md
```

Après un `mv` ou un `cp -p` vers un répertoire collaboratif, repassez donc un
`chgrp`.

Le compte `root`, lui, n'échappe pas à la règle : un fichier qu'il crée dans le
répertoire hérite du groupe comme les autres.

```bash
sudo touch /srv/chantier/rapport-root.md
sudo ls -l /srv/chantier/rapport-root.md
```

```text
-rw-r--r--. 1 root redaction 0 Jul 22 12:21 /srv/chantier/rapport-root.md
```

### Empêcher les suppressions croisées : le sticky bit

Un répertoire inscriptible par le groupe laisse chaque membre supprimer les
fichiers des autres, y compris ceux qu'il ne peut pas modifier :

```bash
sudo -u pierre rm /srv/chantier/note.md      # passe sans broncher
```

Supprimer un fichier est un droit d'écriture sur le **répertoire**, pas sur le
fichier. Le guide traite ce cas pour les répertoires inscriptibles et donne le
remède, le **sticky bit** (`chmod a+t`, ou le `1` de tête), qu'il illustre par
`/tmp` et `/var/tmp` en `1777`, vérifiés ici :

```bash
ls -ld /tmp /var/tmp
```

```text
drwxrwxrwt.  9 root root 4096 Jul 22 12:20 /tmp
drwxrwxrwt. 10 root root 4096 Jul 22 12:20 /var/tmp
```

Il se combine sans difficulté avec le set-GID :

```bash
sudo chmod +t /srv/chantier
sudo stat -c '%a %A' /srv/chantier
sudo -u pierre rm /srv/chantier/plan.md
```

```text
3770 drwxrws--T
rm: cannot remove '/srv/chantier/plan.md': Operation not permitted
```

Le mode est passé à `3770` : `2` pour le set-GID, plus `1` pour le sticky bit.
`man chmod` appelle ce dernier le *restricted deletion flag* et le définit
ainsi : il empêche les utilisateurs non privilégiés de supprimer ou de renommer
un fichier du répertoire, à moins qu'ils ne possèdent le fichier ou le
répertoire. Chacun reste donc maître de ses propres fichiers :

```bash
sudo -u pierre sh -c 'umask 007; touch /srv/chantier/relecture.md'
sudo -u pierre rm /srv/chantier/relecture.md      # passe : c'est son fichier
```

Le `T` **majuscule** de `drwxrws--T` obéit à la même règle que le `S` : le
sticky bit s'affiche à la place du `x` des « autres », et il est en majuscule
parce qu'ici les « autres » n'ont pas ce `x`. Sur `/tmp`, ouvert à tous, c'est
un `t` minuscule.

Un dernier détail, cohérent avec ce qu'on a vu sur `chmod` numérique : passez
le `chmod -R 770` vu plus haut sur ce répertoire désormais en `3770`, et le
mode retombe à `2770`. Le sticky bit, lui, est bien **effacé** par un mode
numérique, là où le set-GID survit. Les deux bits ne sont pas traités pareil.

### Inventorier les bits posés

Le guide donne la recherche des binaires setuid et setgid, à comparer à une
liste de référence :

```bash
sudo find / -xdev -type f \( -perm -4000 -o -perm -2000 \) | sort
```

Sur cette VM AlmaLinux 10, elle renvoie une liste courte et légitime :

```text
/usr/bin/chage
/usr/bin/chfn
/usr/bin/chsh
/usr/bin/crontab
/usr/bin/gpasswd
/usr/bin/mount
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/pkexec
/usr/bin/su
/usr/bin/sudo
/usr/bin/umount
/usr/bin/write
/usr/lib/polkit-1/polkit-agent-helper-1
/usr/libexec/utempter/utempter
/usr/sbin/grub2-set-bootflag
/usr/sbin/mount.nfs
/usr/sbin/pam_timestamp_check
/usr/sbin/unix_chkpwd
```

Ne confondez pas les deux usages du même bit : cette commande cible `-type f`,
donc les **exécutables**, où le setgid fait tourner le programme avec les
privilèges de son groupe. Elle ne verra jamais vos répertoires collaboratifs.
Pour ceux-là, c'est `-type d` :

```bash
sudo find /srv -xdev -type d -perm -2000
```

```text
/srv/chantier
/srv/chantier/brouillons
```

Un seul bit, deux significations : sur un exécutable, c'est une élévation de
privilèges à surveiller ; sur un répertoire, un simple héritage de groupe. Le
guide rappelle qu'on ne retire jamais un bit setuid ou setgid en masse : on
inventorie, on documente, on compare à une liste de référence.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Les nouveaux fichiers ne sont pas au bon groupe | le bit set-GID n'est pas posé sur le répertoire, ou il l'a été après leur création |
| `ls -ld` montre un `S` majuscule | le groupe n'a pas le droit `x` sur le répertoire : `chmod g+x` |
| Le bit set-GID est toujours là après un `chmod 0755` | sur un répertoire, `chmod` numérique le préserve : passer par `g-s`, `00755` ou `=755` |
| Le groupe est bon mais un membre a `Permission denied` en écriture | l'UMASK du créateur a retiré `g+w` : `022` et `027` le retirent, `007` et `002` non |
| Un fichier arrivé par `mv` garde son ancien groupe | `mv` renomme, il ne crée pas : le set-GID ne s'applique pas. Idem avec `cp -p` |
| Les fichiers d'avant n'ont pas changé de groupe | l'héritage ne vaut que pour le futur : `chgrp -R`, puis `chmod -R g+w` |
| Tous les fichiers sont devenus exécutables | un `chmod -R` numérique est passé : utiliser la forme symbolique |
| Un membre supprime les fichiers des autres | c'est un droit d'écriture sur le répertoire : poser le sticky bit (`chmod +t`) |
| `Permission denied` sur un simple `ls` du répertoire | votre compte n'est pas membre du groupe et le répertoire est en `0770` : passer par `sudo` |

Pour tout défaire et repartir de zéro :

```bash
sudo rm -rf /srv/chantier
sudo userdel -r nadia
sudo userdel -r pierre
sudo groupdel redaction
sudo rm -f /etc/profile.d/99-chantier-demo.sh
```

Le dernier `rm` n'est pas un détail : un fichier laissé dans `/etc/profile.d/`
continue de changer l'UMASK de **tous** les comptes de la machine, longtemps
après que le répertoire de démonstration a disparu.

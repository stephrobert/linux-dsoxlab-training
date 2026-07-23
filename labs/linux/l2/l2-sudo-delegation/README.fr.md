# Lab — déléguer un sudo limité

## Rappel

[**sudo sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/)

Mets la politique sudo dans des drop-ins `/etc/sudoers.d/` (mode `0440`). Une
règle se lit `qui où=(en-tant-que) commandes` ; `%groupe` cible un groupe,
`NOPASSWD:` supprime la demande de mot de passe, et lister des commandes
explicites, c'est le moindre privilège. **Toujours** valider avec
`visudo -cf <fichier>` — une erreur de syntaxe peut casser tout sudo.
`sudo -l -U <user>` montre la politique effective.

## Le cours

Les exemples ci-dessous délèguent des commandes de sauvegarde au groupe
`sauvegarde` et à l'utilisatrice `nadia`, dans le drop-in
`/etc/sudoers.d/30-sauvegarde` : le challenge, lui, vous demandera un autre
groupe, un autre compte, un autre fichier et d'autres commandes. Le but est
d'apprendre la méthode et de savoir la prouver, pas de recopier une ligne.

Toutes les sorties viennent d'une AlmaLinux 10.2 avec `sudo 1.9.17p2`. Le nom
d'hôte affiché sera le vôtre.

> Avant votre première modification, ouvrez une **seconde session SSH** et
> laissez-la ouverte. Une configuration sudoers cassée se répare depuis un shell
> déjà authentifié, pas depuis un terminal qui vient de perdre `sudo`.

### Le décor de démonstration

```bash
sudo groupadd sauvegarde
sudo useradd -m -G sauvegarde nadia
id nadia
sudo -l -U nadia
```

```text
uid=1002(nadia) gid=1003(nadia) groups=1003(nadia),1002(sauvegarde)
User nadia is not allowed to run sudo on atelier.
```

Appartenir à un groupe ne donne rien tant qu'aucune règle ne nomme ce groupe.
Relevez aussi ce qui est déjà en place, pour ne pas l'écraser :

```bash
sudo ls -l /etc/sudoers.d/ ; sudo grep -n includedir /etc/sudoers
```

```text
-r--r-----. 1 root root 188 Jul 22 13:30 90-cloud-init-users
120:#includedir /etc/sudoers.d
```

Ce fichier `90-cloud-init-users` porte le sudo des comptes d'administration de
la VM : n'y touchez pas, écrivez toujours dans **votre** fichier. Notez qu'
AlmaLinux 10 utilise encore la forme historique `#includedir`, pas
`@includedir` : les deux fonctionnent.

### Écrire la règle, la valider, et vérifier qu'elle est bien lue

Une règle tient sur une ligne, `qui hôte=(cible) commandes`, les commandes en
**chemin absolu**. Écrivez d'abord le fichier ailleurs que dans
`/etc/sudoers.d/`, et validez-le avant de l'installer :

```bash
cat -n /tmp/30-sauvegarde.bad
sudo visudo -c -f /tmp/30-sauvegarde.bad ; echo "rc=$?"
```

```text
     1	# Delegation sauvegarde
     2	Cmnd_Alias TAILLES = /usr/bin/du
     3	%sauvegarde ALL=(root) NOPASSWD /usr/bin/du

/tmp/30-sauvegarde.bad:3:44: syntax error
%sauvegarde ALL=(root) NOPASSWD /usr/bin/du
                                           ^
rc=1
```

Le message donne le **fichier**, la **ligne**, la **colonne** et un curseur.
Ici, il manque le deux-points de `NOPASSWD:`. Tant que `rc` vaut 1, ce fichier
n'a rien à faire dans `/etc/sudoers.d/`.

Corrigé, il s'installe avec `visudo -f`, qui édite en place et valide à
l'enregistrement :

```bash
sudo visudo -f /etc/sudoers.d/30-sauvegarde
sudo ls -l /etc/sudoers.d/30-sauvegarde
sudo visudo -c ; echo "rc=$?"
```

```text
-rw-r-----. 1 root root 77 Jul 22 14:57 /etc/sudoers.d/30-sauvegarde

/etc/sudoers.d/30-sauvegarde: bad permissions, should be mode 0440
/etc/sudoers: parsed OK
/etc/sudoers.d/90-cloud-init-users: parsed OK
rc=1
```

Premier piège, contre-intuitif : `visudo -f` a posé `0640`, pas `0440`. sudo
s'en contente et applique la règle, mais `visudo -c` refuse de valider : le
fichier fautif n'obtient **pas** son `parsed OK` et le code de retour passe à 1.
Un `chmod 0440` suffit, et les trois fichiers repassent au vert :

```bash
sudo chmod 0440 /etc/sudoers.d/30-sauvegarde
sudo visudo -c ; echo "rc=$?"
```

```text
/etc/sudoers: parsed OK
/etc/sudoers.d/30-sauvegarde: parsed OK
/etc/sudoers.d/90-cloud-init-users: parsed OK
rc=0
```

Deuxième piège, plus vicieux : un drop-in peut être **ignoré en silence**. Le
même fichier, nommé `30-sauvegarde.conf` :

```bash
sudo visudo -c ; echo "rc=$?" ; sudo -l -U nadia
```

```text
/etc/sudoers: parsed OK
/etc/sudoers.d/90-cloud-init-users: parsed OK
rc=0
User nadia is not allowed to run sudo on atelier.
```

`visudo -c` renvoie 0 et ne mentionne même pas le fichier : un nom contenant un
point, ou finissant par `~`, est sauté sans le moindre avertissement. Renommé
sans point, il réapparaît dans la liste et la règle prend effet. Un fichier
laissé en `0666` est écarté de la même façon, à un message près
(`sudo: /etc/sudoers.d/30-sauvegarde is world writable`).

D'où le réflexe : après chaque dépôt de fichier, ne supposez rien, demandez à
sudo ce qu'il a compris avec `sudo -l -U <user>`.

### NOPASSWD, et le refus quand rien ne matche

Sans le tag `NOPASSWD:`, la règle exige le mot de passe de l'appelante :

```text title="/etc/sudoers.d/30-sauvegarde"
Cmnd_Alias TAILLES = /usr/bin/du -sh /var/log
%sauvegarde ALL=(root) TAILLES
```

```bash
sudo -u nadia sudo -n du -sh /var/log
```

```text
sudo: a password is required
```

`sudo -n` (*non interactive*) refuse de demander quoi que ce soit : c'est le
moyen de prouver qu'un mot de passe **serait** réclamé. Ajoutez le tag
(`%sauvegarde ALL=(root) NOPASSWD: TAILLES`) :

```bash
sudo -l -U nadia | tail -2 ; sudo -u nadia sudo -n du -sh /var/log
```

```text
    (root) NOPASSWD: /usr/bin/du -sh /var/log
5.7M	/var/log
```

L'alias a été **résolu** : sudo affiche la commande réelle, pas l'étiquette.
La délégation est bien étroite, le moindre argument différent ne matche plus :
`sudo -u nadia sudo -n du -sh /var/log/dnf` répond `sudo: a password is
required`, et un chemin sans rapport comme `du -sh /etc` donne exactement la
même réponse.

**Ce message trompe.** On attendrait un refus explicite ; sudo réclame d'abord
le mot de passe, car `NOPASSWD:` ne vaut que pour les commandes **effectivement
matchées**. Une fois l'utilisatrice authentifiée sur ce second essai, le vrai
verdict tombe :

```text
Sorry, user nadia is not allowed to execute '/bin/du -sh /etc' as root on atelier.lab.
```

Retenez que `sudo: a password is required` ne dit **rien** sur vos droits : seul
`sudo -l -U` répond à cette question. Notez au passage `/bin/du` là où la règle
dit `/usr/bin/du` : sur cette distribution `/bin` est un lien symbolique vers
`usr/bin`, et sudo travaille sur le chemin résolu.

### La dernière règle qui matche gagne

Contrairement au réflexe « premier match » des pare-feux, sudo applique la
**dernière** correspondance. Deux fichiers ne différant que par l'ordre :

```text title="Ordre A : interdiction puis autorisation"
%sauvegarde ALL=(root) NOPASSWD: !/usr/bin/find
%sauvegarde ALL=(root) NOPASSWD: /usr/bin/du, /usr/bin/find
```

`sudo -u nadia sudo -n find /var/log -maxdepth 0` affiche `/var/log` :
l'interdiction est **annulée** par la règle permissive qui la suit. On inverse
les deux lignes, sans rien changer d'autre :

```text title="Ordre B : autorisation puis interdiction"
%sauvegarde ALL=(root) NOPASSWD: /usr/bin/du, /usr/bin/find
%sauvegarde ALL=(root) NOPASSWD: !/usr/bin/find
```

```text
Sorry, user nadia is not allowed to execute '/bin/find /var/log -maxdepth 0' as root on atelier.lab.
```

Même politique écrite, résultat inverse. Cela vaut aussi **entre fichiers** de
`/etc/sudoers.d/`, lus en ordre lexical : d'où la convention du préfixe
numérique (`30-`, `90-`) pour maîtriser cet ordre.

### Ce que déléguer un binaire donne vraiment

Une règle peut sembler restrictive et rendre root quand même. Déléguez `find`
nu :

```text
%sauvegarde ALL=(root) NOPASSWD: /usr/bin/du, /usr/bin/find
```

```bash
sudo -u nadia sudo -n find /var/log -maxdepth 0 -exec id \;
```

```text
uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:...
```

`find` sait lancer d'autres programmes : déléguer une commande de recherche vaut
déléguer **root entier**. `vim`, `less`, `awk` et `tar` partagent ce défaut.
Imposer les arguments referme la porte : avec la règle
`/usr/bin/find /var/log -name *.log`, la recherche prévue passe et le
`-exec id \;` retombe sur `sudo: a password is required`, faute de matcher.

Le cas de l'éditeur mérite sa propre démonstration, car c'est le plus fréquent.
Avec `/usr/bin/vi` délégué, l'éditeur tourne en root, et son évasion `:!` aussi :

```bash
sudo -u nadia sudo -n vi -es -c ':!id > /tmp/preuve-vi.txt' -c ':q!' /etc/motd
cat /tmp/preuve-vi.txt
```

```text
uid=0(root) gid=0(root) groups=0(root) [...]
```

`sudoedit` renverse la mécanique : seul le remplacement final du fichier est
privilégié, l'éditeur, lui, tourne sous **votre** identité. Avec la règle
`%sauvegarde ALL=(root) NOPASSWD: sudoedit /etc/motd` et un faux éditeur qui se
contente d'écrire la sortie d'`id` dans un fichier :

```bash
sudo -u nadia env SUDO_EDITOR=/tmp/faux-editeur.sh sudoedit -n /etc/motd
cat /tmp/preuve-editeur.txt
```

```text
uid=1002(nadia) gid=1003(nadia) groups=1003(nadia),1002(sauvegarde) [...]
```

Deux règles qui se ressemblent, deux niveaux de privilège opposés. Pour laisser
modifier un fichier, c'est toujours `sudoedit`, jamais `sudo <editeur>`.

### Defaults : le mot de passe qui ne revient pas, et la trace

sudo ne redemande pas le mot de passe pendant quelques minutes : il garde un
**timestamp** de la session authentifiée. Deux appels d'affilée dans le même
shell, avec une règle **sans** `NOPASSWD:` :

```text
uid=0(root)                            <- 1er appel, mot de passe saisi
--- 2e appel, sans mot de passe ---
uid=0(root)
```

Ce délai se règle par un `Defaults`, qui peut ne viser qu'une utilisatrice :

```text title="/etc/sudoers.d/30-sauvegarde"
Defaults:nadia timestamp_timeout=0
Defaults:nadia logfile=/var/log/sudo-sauvegarde.log
%sauvegarde ALL=(root) /usr/bin/id
```

```bash
sudo -l -U nadia | head -3
```

```text
Matching Defaults entries for nadia on atelier:
    !visiblepw, always_set_home, [...] secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin,
    timestamp_timeout=0, logfile=/var/log/sudo-sauvegarde.log
```

Avec `timestamp_timeout=0`, le second appel redemande le mot de passe
(`sudo: a password is required`). Et `logfile` détourne le journal vers un
fichier dédié, autorisations comme refus :

```bash
sudo cat /var/log/sudo-sauvegarde.log
```

```text
Jul 22 15:00:22 : nadia : PWD=/home/ansible ; USER=root ; COMMAND=/usr/bin/id
Jul 22 15:00:22 : nadia : a password is required ; PWD=/home/ansible ; USER=root
    ; COMMAND=/usr/bin/id
```

Sans ce `Defaults`, tout part dans le journal système, où le verdict se lit
aussi bien : `sudo journalctl -t sudo --no-pager | tail -2` y affiche par
exemple `nadia : command not allowed ; ... ; COMMAND=/bin/du -sh /etc`.

Un dernier `Defaults` vaut d'être connu : `requiretty`, qui interdit à sudo de
s'exécuter sans terminal. Il n'apparaît **pas** dans les `Matching Defaults`
ci-dessus, et c'est bien pour cela que toutes les commandes de ce cours ont pu
tourner à travers `ssh <hôte> 'commande'`, sans tty.

### Dépannage et remise à zéro

| Symptôme | Cause probable |
|---|---|
| `X is not allowed to run sudo` alors que le fichier existe | nom contenant un `.` ou finissant par `~` : le fichier est sauté en silence |
| `bad permissions, should be mode 0440`, `visudo -c` en `rc=1` | droits du drop-in ; `visudo -f` laisse `0640`, corriger par `chmod 0440` |
| `is world writable` | drop-in en `0666` : sudo l'ignore complètement |
| `sudo: a password is required` malgré une règle `NOPASSWD:` | la commande tapée ne matche pas la règle (argument en trop, chemin différent) |
| `Sorry, user ... is not allowed to execute ...` | la règle ne couvre pas cette commande ; comparer avec `sudo -l -U <user>` |
| Une interdiction `!` reste sans effet | une règle permissive matche **après** : la dernière gagne |
| `syntax error` avec ligne et colonne | relire le caractère pointé par le curseur (souvent le `:` de `NOPASSWD:`) |
| La règle semble bonne mais rien ne change | chemin non absolu, ou différent du réel : vérifier avec `command -v <binaire>` |

Pour tout défaire et repartir de zéro :

```bash
sudo rm -f /etc/sudoers.d/30-sauvegarde /var/log/sudo-sauvegarde.log
sudo userdel -r nadia
sudo groupdel sauvegarde
sudo visudo -c
sudo -l
```

Les deux dernières commandes ne sont pas facultatives : elles prouvent que la
configuration sudoers est de nouveau saine et que **votre** accès administrateur
est intact.

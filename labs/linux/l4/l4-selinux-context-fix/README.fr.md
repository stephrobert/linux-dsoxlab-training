# Lab — corriger un contexte SELinux durablement

## Rappel

[**SELinux sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Chaque fichier porte un **type** SELinux. Un service confiné ne touche que les
fichiers dont le type est autorisé par sa politique : un démon de journalisation
écrit dans du `var_log_t`, une base de données dans son propre type, et ainsi de
suite. `chcon` pose une étiquette mais un réétiquetage la perd ;
`semanage fcontext -a -t <type> "<regex-chemin>"` écrit une règle persistante et
`restorecon -Rv <chemin>` l'applique. `ls -Z` montre le type actif.

## Le cours

Les exemples ci-dessous portent volontairement sur autre chose que le challenge :
on y fait écrire un journal applicatif par `rsyslog` dans un répertoire maison,
`/opt/journaux-appli`. Vous apprenez la méthode et vous la transposez, vous ne
recopiez pas une ligne.

Toutes les sorties reproduites ici ont été obtenues sur une AlmaLinux 10 en mode
enforcing.

### Première vérification : SELinux est-il vraiment actif ?

Rien de ce qui suit ne se démontre si SELinux ne fait pas respecter sa politique.
C'est donc la première commande, avant tout diagnostic :

```bash
getenforce
```

```text
Enforcing
```

`sestatus` donne la vue complète, et surtout deux lignes qu'il faut savoir
distinguer :

```text
SELinux status:                 enabled
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
```

`Current mode` est le mode **en cours** (celui que `setenforce` change) ;
`Mode from config file` est celui que la machine reprendra **au prochain
démarrage**, lu dans `/etc/selinux/config`. Les deux peuvent diverger, et c'est
exactement ce qui fait qu'un serveur « qui marche » cesse de marcher après un
redémarrage.

> `setenforce 0` bascule en permissive : SELinux continue de journaliser mais ne
> bloque plus rien. C'est un outil de diagnostic, à repasser à `1` tout de suite
> après. En revanche, ne touchez **jamais** à `SELINUX=` dans
> `/etc/selinux/config` pour contourner un refus : vous ne réglez rien, vous
> désarmez la machine, et sur RHEL 9 et suivants revenir de `disabled` à
> `enforcing` impose un réétiquetage complet du disque.

La politique chargée ici est `targeted` : seuls les services listés dans la
politique sont confinés, le reste tourne en `unconfined_t`.

### Lire une étiquette : quatre champs, un seul qui décide

Un contexte s'écrit `utilisateur:rôle:type:niveau`. Il se lit sur trois objets
différents, avec trois commandes :

```bash
ls -Zd /opt/journaux-appli      # un fichier ou un répertoire
ps -eZ | grep rsyslogd          # un processus
id -Z                           # votre propre shell
```

```text
unconfined_u:object_r:usr_t:s0 /opt/journaux-appli
system_u:system_r:syslogd_t:s0    25554 ?        00:00:00 rsyslogd
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

Détaillons le premier : `unconfined_u` est l'utilisateur SELinux (sans rapport
avec l'utilisateur Unix propriétaire), `object_r` le rôle (invariablement
`object_r` sur un fichier), `usr_t` le **type**, `s0` le niveau MLS.

**Dans la quasi-totalité du travail quotidien, seul le type compte.** C'est lui
que la politique croise : ici, un processus en `syslogd_t` face à un répertoire
en `usr_t`. Les trois autres champs, vous les lirez sans les modifier.

Le troisième affichage mérite une remarque : votre shell est `unconfined_t`,
c'est-à-dire non confiné. Vous ne rencontrerez donc jamais de refus SELinux en
tapant des commandes vous-même, ce qui explique pourquoi le problème semble
toujours venir « du service » et jamais de vous.

### Le refus : « Permission denied » avec des droits Unix parfaits

Montons le décor. On crée un répertoire et on demande à `rsyslog` d'y déposer les
messages de la facilité `local5` :

```bash
sudo mkdir -p /opt/journaux-appli
printf 'local5.*  /opt/journaux-appli/atelier.log\n' | sudo tee /etc/rsyslog.d/99-atelier.conf
sudo systemctl restart rsyslog
logger -p local5.info "message de test"
```

Rien n'arrive dans le répertoire. Pourtant les droits Unix sont irréprochables,
et `rsyslogd` tourne en root :

```bash
ls -ld /opt/journaux-appli
```

```text
drwxr-xr-x. 2 root root 6 Jul 22 15:58 /opt/journaux-appli
```

Le service, lui, se plaint d'une permission refusée :

```bash
sudo journalctl -u rsyslog --since -1min | grep -i "open error"
```

```text
rsyslogd[25441]: file '/opt/journaux-appli/atelier.log': open error: Permission denied
```

C'est le message déroutant par excellence : root, `drwxr-xr-x`, et pourtant
refusé. Le point Unix étant écarté, la réponse est dans le journal d'audit :

```bash
sudo ausearch -m avc --success no -ts recent
```

```text
type=AVC msg=audit(1784736057.748:15868): avc:  denied  { write } for  pid=26086
  comm=72733A6D61696E20513A526567 name="journaux-appli" dev="vda4" ino=8590658
  scontext=system_u:system_r:syslogd_t:s0
  tcontext=unconfined_u:object_r:usr_t:s0 tclass=dir permissive=0
```

Quatre informations suffisent à conclure : `denied { write }` est l'opération
interdite, `scontext=...:syslogd_t` le type du **processus** demandeur,
`tcontext=...:usr_t` le type de la **cible** refusée, et `tclass=dir` la nature
de cette cible. `permissive=0` confirme que le refus a bien été **appliqué** et pas seulement
journalisé. Le `comm=` en hexadécimal n'est pas un bug : `ausearch` encode ainsi
les noms contenant des caractères spéciaux, ici le nom de thread `rs:main Q:Reg`.

`audit2why` traduit la même ligne :

```bash
sudo ausearch -m avc --success no -ts recent | audit2why
```

```text
	Was caused by:
		Missing type enforcement (TE) allow rule.

		You can use audit2allow to generate a loadable module to allow this access.
```

Prenez cette suggestion pour ce qu'elle est : la **dernière** des trois options.
On corrige d'abord l'étiquette, puis on cherche un booléen, et seulement en
dernier recours on génère un module.

> Sur cette machine, `sealert` n'est pas disponible : `rpm -q setroubleshoot-server`
> répond `package setroubleshoot-server is not installed`. C'est le cas de toute
> installation minimale, et c'est aussi le cas en examen. Savoir lire l'AVC brut
> n'est donc pas un pis-aller, c'est la compétence attendue. Si le paquet est
> installé, `journalctl -t setroubleshoot` reprend les mêmes refus en clair.

### Quel type ce chemin devrait-il porter ?

Devant un refus, la vraie question n'est pas « quel type mettre » mais « quel
type la politique attend-elle ici ». `matchpathcon` répond sans rien modifier :

```bash
matchpathcon /opt/journaux-appli /var/log/messages
```

```text
/opt/journaux-appli	system_u:object_r:usr_t:s0
/var/log/messages	system_u:object_r:var_log_t:s0
```

Le verdict est net : notre répertoire hérite de `usr_t` (le type par défaut sous
`/opt`), alors qu'un journal se range en `var_log_t`. C'est le décalage exact que
l'AVC signalait.

Deuxième méthode, utile quand on cherche un précédent : interroger la base des
contextes, qui compte ici près de six mille règles (`grep` est indispensable).

```bash
sudo semanage fcontext -l | grep -w var_log_t | head -2
```

```text
/nsr/logs(/.*)?                                    all files          system_u:object_r:var_log_t:s0
/opt/zimbra/log(/.*)?                              all files          system_u:object_r:var_log_t:s0
```

Ces lignes montrent au passage la forme d'une règle : une **expression
rationnelle** de chemin, une classe de fichiers, un contexte.

### `chcon` : correct tout de suite, perdu au premier `restorecon`

`chcon` écrit l'étiquette directement sur l'inode. L'effet est immédiat :

```bash
sudo chcon -t var_log_t /opt/journaux-appli
sudo systemctl restart rsyslog
logger -p local5.info "premier essai"
sudo ls -lZ /opt/journaux-appli/
```

```text
-rw-------. 1 root root system_u:object_r:var_log_t:s0 68 Jul 22 16:00 atelier.log
```

Le journal est écrit, le fichier créé hérite du type du répertoire. Tout semble
réglé. Maintenant, la vérification qui compte :

```bash
sudo restorecon -Rv /opt/journaux-appli
```

```text
Relabeled /opt/journaux-appli from unconfined_u:object_r:var_log_t:s0 to unconfined_u:object_r:usr_t:s0
Relabeled /opt/journaux-appli/atelier.log from system_u:object_r:var_log_t:s0 to system_u:object_r:usr_t:s0
```

Tout est défait. Et le service retombe en panne :

```text
rsyslogd[25902]: file '/opt/journaux-appli/atelier.log': open error: Permission denied
```

**La raison tient en une phrase : `chcon` ne modifie pas la politique.** Il pose
une étiquette sur un objet, sans écrire nulle part que ce chemin la mérite. Dès
que quelque chose consulte la référence, l'étiquette est jugée fausse et
corrigée. Or ce « quelque chose » arrive tout seul : un `restorecon` lancé par un
paquet ou un script, un `/.autorelabel` au démarrage, une restauration après
sauvegarde. Le service tient des semaines, puis tombe à un redémarrage sans que
personne n'ait rien changé. Réservez donc `chcon` au test rapide qui confirme un
diagnostic, comme on vient de le faire.

### `semanage fcontext` + `restorecon` : la correction qui tient

La correction durable se fait en deux temps, et les deux sont indispensables :
`semanage fcontext -a` **écrit la règle**, `restorecon` **l'applique** aux
fichiers déjà présents.

```bash
sudo semanage fcontext -a -t var_log_t "/opt/journaux-appli(/.*)?"
```

Rien ne s'affiche, mais la référence a changé. `matchpathcon` le confirme avant
même qu'un seul fichier ait bougé :

```text
/opt/journaux-appli/atelier.log	system_u:object_r:var_log_t:s0
```

Notez la forme du chemin : `"/opt/journaux-appli(/.*)?"` est une expression
rationnelle, entre guillemets pour que le shell n'y touche pas. Le `(/.*)?` final
signifie « ce répertoire, et éventuellement tout ce qui est dessous ». Sans lui,
la règle ne couvrirait que le répertoire lui-même.

On applique :

```bash
sudo restorecon -Rv /opt/journaux-appli
```

```text
Relabeled /opt/journaux-appli from unconfined_u:object_r:usr_t:s0 to unconfined_u:object_r:var_log_t:s0
```

Le service écrit de nouveau. Et cette fois, le test qui avait tué le `chcon` ne
change plus rien :

```bash
sudo restorecon -Rv /opt/journaux-appli   # aucune ligne : rien à corriger
sudo ls -ldZ /opt/journaux-appli
```

```text
drwxr-xr-x. 2 root root unconfined_u:object_r:var_log_t:s0 25 Jul 22 16:00 /opt/journaux-appli
```

Deux commandes prouvent que la règle est bien dans la politique, et pas seulement
sur le disque. `-C` restreint l'affichage aux règles **locales**, celles que vous
avez ajoutées :

```bash
sudo semanage fcontext -l -C
```

```text
SELinux fcontext                                   type               Context

/opt/journaux-appli(/.*)?                          all files          system_u:object_r:var_log_t:s0
```

Elle est stockée dans un fichier qu'on ne modifie jamais à la main :

```text
# /etc/selinux/targeted/contexts/files/file_contexts.local
# This file is auto-generated by libsemanage
# Do not edit directly.

/opt/journaux-appli(/.*)?    system_u:object_r:var_log_t:s0
```

C'est là toute la différence : `chcon` écrivait sur l'inode, `semanage fcontext`
écrit ici. Un réétiquetage complet relit ce fichier, donc la correction survit.

### Défaire proprement

Une règle locale se retire avec `-d`, en répétant **exactement** l'expression
utilisée à l'ajout. Le retrait ne réétiquette rien : il faut relancer
`restorecon`, qui applique alors le type par défaut retrouvé.

```bash
sudo semanage fcontext -d "/opt/journaux-appli(/.*)?"
sudo restorecon -Rv /opt/journaux-appli
```

```text
Relabeled /opt/journaux-appli from unconfined_u:object_r:var_log_t:s0 to unconfined_u:object_r:usr_t:s0
```

Deux contrôles pour clore : la liste des règles locales doit être vide, et
SELinux toujours en enforcing.

```bash
sudo semanage fcontext -l -C   # aucune ligne
getenforce                     # Enforcing
```

**Le réflexe à garder.** Devant un service qui refuse un fichier alors que
`ls -l` semble correct :

1. `getenforce` : SELinux est-il en cause ?
2. `ausearch -m avc --success no -ts recent` : lire `scontext`, `tcontext`,
   l'opération et `permissive=`.
3. `matchpathcon <chemin>` : quel type la politique attend-elle ?
4. Si le type actif est faux mais la politique juste : `restorecon -Rv`.
5. Si la politique elle-même ignore ce chemin :
   `semanage fcontext -a -t <type> "<chemin>(/.*)?"` puis `restorecon -Rv`.
6. `chcon` uniquement pour confirmer une hypothèse, jamais comme correction.

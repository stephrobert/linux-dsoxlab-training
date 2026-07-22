# Lab — diagnostiquer un refus AVC SELinux

## Rappel

[**SELinux sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Quand un service confiné se voit refuser un accès, SELinux consigne un **AVC**
dans le journal d'audit. `ausearch -m avc` l'en extrait, `audit2why` l'explique,
`sealert` le traduit en clair quand il est installé. L'AVC nomme le domaine qui
agit (`scontext`), l'objet visé (`tcontext`), la classe de cet objet (`tclass`)
et l'opération refusée : ces quatre champs suffisent à désigner la correction.
`ls -Z` montre l'étiquette d'un fichier, `getenforce` le mode courant. Jamais
`setenforce 0`.

## Le cours

Les exemples ci-dessous portent volontairement sur autre chose que le challenge :
on y diagnostique un `chronyd` qui refuse de démarrer, puis une connexion SSH qui
**réussit** malgré un refus journalisé. Vous apprenez à lire un AVC, vous ne
recopiez pas une ligne.

Ce cours ne traite ni la correction d'étiquette ni les booléens : ce sont les
sujets des labs `l4-selinux-context-fix` et `l4-selinux-boolean-port`. Ici, on
s'arrête au moment où l'AVC a dit quoi corriger, parce que c'est là que tout se
joue. Toutes les sorties reproduites ont été relevées sur une AlmaLinux 10.2 en
mode enforcing.

### Où les refus sont écrits, et où ils ne sont pas

Première question, toujours la même : SELinux fait-il respecter sa politique ?

```bash
getenforce
```

```text
Enforcing
```

En `Permissive`, tout ce qui suit s'écrit encore dans le journal mais rien n'est
bloqué : votre panne vient alors d'ailleurs. Pour trancher, on bascule avec
`setenforce 0` / `setenforce 1`, et **jamais** en touchant `/etc/selinux/config`,
qui ne joue qu'au prochain démarrage.

Les refus partent du noyau vers `auditd`, qui les écrit dans
**`/var/log/audit/audit.log`**. Le guide propose aussi un raccourci,
`dmesg | grep -i denied`. Vérifions-le :

```bash
sudo dmesg | grep -ic denied
sudo grep -c "avc:  denied" /var/log/audit/audit.log
```

```text
0
71
```

**Zéro dans `dmesg`, soixante et onze dans le journal d'audit.** Quand `auditd`
tourne, il capte les messages, qui ne restent pas dans le tampon du noyau : ne
concluez jamais « pas de refus » sur le silence de `dmesg`.

### Le symptôme : une panne banale, sans rien d'anormal dans les droits

Mettons en place la panne. Un administrateur retouche la configuration de
`chronyd` depuis son répertoire personnel, puis la remet en place avec `mv` :

```bash
cp /etc/chrony.conf ~/chrony.conf
printf '# ajustement atelier\n' >> ~/chrony.conf
sudo mv ~/chrony.conf /etc/chrony.conf
sudo systemctl restart chronyd
```

```text
Job for chronyd.service failed because the control process exited with error code.
```

Le service dit ensuite ce qu'il sait dire :

```bash
sudo journalctl -u chronyd --since -3min | tail -3
```

```text
chronyd[26618]: Fatal error : Could not open /etc/chrony.conf : Permission denied
systemd[1]: chronyd.service: Main process exited, code=exited, status=1/FAILURE
[...]
```

« Permission denied », et pourtant, côté Unix, rien à redire : le fichier est
lisible par tous et `chronyd` démarre en root.

```bash
ls -lZ /etc/chrony.conf
```

```text
-rw-r--r--. 1 root root unconfined_u:object_r:user_home_t:s0 1406 Jul 22 16:09 /etc/chrony.conf
```

Le `.` après les droits signale un contexte SELinux, et `ls -Z` le donne :
`user_home_t`. Le `mv` a **conservé l'étiquette de la source**, contrairement à
une copie, qui aurait pris celle du répertoire de destination : c'est l'origine
la plus fréquente des refus rencontrés en production. Mais à ce stade nous ne
faisons que soupçonner ; la preuve est dans l'AVC.

### Sortir l'AVC du journal, et le piège du terminal

La commande de référence :

```bash
sudo ausearch -m avc -ts recent
```

```text
<no matches>
```

Réponse fausse : le journal contient 71 refus. `ausearch` se comporte ainsi
lorsqu'il n'a **pas de terminal**, exactement le cas d'un `ssh machine
'commande'`, d'un script ou d'un outil d'automatisation. Deux parades :

```bash
sudo ausearch -m avc -ts recent --input-logs   # lit les fichiers journaux
ssh -tt machine 'sudo ausearch -m avc -ts recent'   # force un terminal
```

Retenez-le : un `<no matches>` obtenu depuis un script ne prouve rien du tout.
Trois options de tri servent ensuite en permanence : `-ts` borne la fenêtre
(`recent` vaut les dix dernières minutes, sinon `today` ou une heure comme
`16:00`), `-c <nom>` filtre sur le `comm=`, c'est-à-dire le nom court du
programme, et `-i` interprète les dates et les valeurs numériques. Avec le filtre
sur le service, le refus apparaît :

```bash
sudo ausearch -m avc -ts recent -c chronyd --input-logs
```

```text
type=AVC msg=audit(1784736582.173:16519): avc:  denied  { read } for  pid=26708
  comm="chronyd" name="chrony.conf" dev="vda4" ino=17207620
  scontext=system_u:system_r:chronyd_t:s0
  tcontext=unconfined_u:object_r:user_home_t:s0 tclass=file permissive=0
```

### Disséquer l'AVC champ par champ

C'est la compétence du lab. Reprenons la ligne :

| Champ | Valeur ici | Ce qu'il dit |
| --- | --- | --- |
| `denied { read }` | `read` | l'**opération** refusée |
| `scontext` | `system_u:system_r:chronyd_t:s0` | **qui agit** : le domaine du processus |
| `tcontext` | `unconfined_u:object_r:user_home_t:s0` | **sur quoi** : l'étiquette de la cible |
| `tclass` | `file` | **quel genre d'objet** : fichier, répertoire, socket… |
| `permissive` | `0` | le refus a été **appliqué** |
| `comm=` | `chronyd` | le nom court du programme demandeur |
| `name=` | `chrony.conf` | le nom de la cible, sans son chemin |

Dans `scontext` et `tcontext`, **seul le troisième champ compte** : `chronyd_t`
d'un côté, `user_home_t` de l'autre. La phrase complète se lit alors comme du
français : *un processus `chronyd_t` a voulu `read` un `file` étiqueté
`user_home_t`, et la politique ne le prévoit pas.*

Deux champs demandent une nuance. `name=` ne donne que le nom de feuille ; le
**chemin complet** n'apparaît, dans un champ `path=`, que pour certains appels
système. Sur la même machine, un autre refus le montre :

```text
avc:  denied  { open } for  pid=27058 comm="sshd-session"
  path="/home/sonde/.ssh/authorized_keys" [...] tclass=file permissive=1
```

Quand `path=` manque, le champ `ino=` suffit à retrouver le fichier :
`sudo find / -xdev -inum <inode>` a répondu ici en moins d'un dixième de seconde.
Quant à `comm=`, il est parfois affiché en hexadécimal : ce n'est pas un
bug mais l'encodage qu'`ausearch` applique aux noms contenant des espaces ou des
caractères spéciaux, et `ausearch -i` les rend lisibles.

### L'opération et la `tclass` désignent la correction

C'est le point à emporter : **le couple opération + `tclass` vous dit quelle
famille de correction chercher**, avant même de savoir quel type poser.

| Opération et classe | Ce qui est en cause | Où corriger |
| --- | --- | --- |
| `{ read }`, `{ write }`, `{ open }`, `{ getattr }` sur `file` ou `dir` | l'**étiquette** d'un fichier ou d'un répertoire | `restorecon`, ou `semanage fcontext` si la politique ignore ce chemin |
| `{ name_bind }` sur `tcp_socket` ou `udp_socket` | un service veut un **port** que son type ne couvre pas | `semanage port` |
| `{ name_connect }`, `{ connectto }` | une **connexion sortante** ou vers une socket | le plus souvent un **booléen** |

Notre AVC tombe dans la première ligne : `{ read }` sur `tclass=file`, donc une
étiquette, ni un port ni un booléen. Ces corrections sont détaillées dans les
labs `l4-selinux-context-fix` et `l4-selinux-boolean-port` ; l'essentiel est ici
d'avoir su **choisir** la bonne ligne à partir de deux mots de l'AVC. Le
diagnostic se vérifie en corrigeant, et le service repart :

```bash
sudo restorecon -v /etc/chrony.conf
sudo systemctl restart chronyd && systemctl is-active chronyd
```

```text
Relabeled /etc/chrony.conf from unconfined_u:object_r:user_home_t:s0 to unconfined_u:object_r:etc_t:s0
active
```

### Le faux positif : un AVC n'est pas toujours un blocage

Voici l'erreur de raisonnement la plus coûteuse, et elle se voit sur cette même
machine. Étiquetons volontairement de travers le fichier de clés d'un compte,
puis connectons-nous avec sa clé :

```bash
sudo chcon -t var_log_t /home/sonde/.ssh/authorized_keys
ssh -i /tmp/cle-sonde sonde@localhost 'echo CONNEXION-OK'
```

```text
CONNEXION-OK
```

**La connexion réussit**, alors que le refus a bel et bien été journalisé :

```text
avc:  denied  { read } for  pid=27058 comm="sshd-session" name="authorized_keys"
  scontext=system_u:system_r:sshd_session_t:s0-s0:c0.c1023
  tcontext=unconfined_u:object_r:var_log_t:s0 tclass=file permissive=1
```

Le champ qui change tout : **`permissive=1`**. Le domaine `sshd_session_t` fait
partie des domaines déclarés permissifs par la politique elle-même :

```bash
sudo semanage permissive -l
```

```text
Builtin Permissive Types

dhcpc_hook_t
systemd_hibernate_resume_t
sshd_session_t
sshd_auth_t
[...]
```

Pour ces domaines, SELinux **journalise sans bloquer**. L'appel système
correspondant le confirme, avec `success=yes exit=0` là où celui de `chronyd`
portait `success=no exit=-13`. Une option d'`ausearch` exploite cette
différence :

```bash
sudo ausearch -m avc -ts today --input-logs | grep -c "type=AVC"
sudo ausearch -m avc -ts today --input-logs | grep "type=AVC" | grep -c "permissive=1"
sudo ausearch -m avc -ts today --success no --input-logs | grep -c "type=AVC"
```

```text
71
24
47
```

71 refus journalisés, dont 24 en `permissive=1` ; `--success no` en retient 47,
soit exactement les 71 moins les 24. **Prenez le réflexe de
`ausearch -m avc --success no`** : sans lui, vous passerez une heure à
« corriger » un AVC qui n'a jamais rien empêché, pendant que la panne est
ailleurs.

### `audit2why`, `audit2allow`, et pourquoi `-M` vient en dernier

`audit2why` prend un AVC sur son entrée standard et le traduit :

```bash
sudo ausearch -m avc --success no -ts recent -c chronyd --input-logs | audit2why
```

```text
	Was caused by:
		Missing type enforcement (TE) allow rule.

		You can use audit2allow to generate a loadable module to allow this access.
```

Il n'y a ici aucune règle à activer : la politique n'a rien qui autorise cet
accès. Quand un **booléen** est en cause, `audit2why` le nomme, et c'est alors la
piste à suivre. Notez sa limite, mesurée plus haut : il produit **le même verdict
sur un AVC `permissive=1`**, sans signaler que l'opération a réussi.

`audit2allow` va plus loin et rédige la règle manquante :

```bash
sudo ausearch -m avc --success no -ts recent -c chronyd --input-logs | audit2allow
```

```text
#============= chronyd_t ==============
allow chronyd_t user_home_t:file read;
```

Lisez cette règle avant tout : elle n'autorise pas `chronyd` à lire *ce*
fichier, elle l'autorise à lire **tout fichier portant le type `user_home_t`** de
la machine, c'est-à-dire l'intégralité des répertoires personnels. Une règle
nomme des types, jamais des chemins. Avec `-M`, `audit2allow` va jusqu'au module
installable :

```bash
cd /tmp && sudo ausearch -m avc --success no -ts recent -c chronyd \
  --input-logs | audit2allow -M atelier-chrony
```

```text
******************** IMPORTANT ***********************
To make this policy package active, execute:

semodule -i atelier-chrony.pp
```

> Cette invitation est un piège. `semodule -i` grave une exception permanente
> dans la politique pour contourner un fichier mal étiqueté qu'un `restorecon`
> aurait réglé en une seconde : le trou reste ouvert longtemps après que
> l'incident est oublié. Le guide classe `audit2allow -M` en **troisième et
> dernière** option, après l'étiquette et le booléen, et impose de lire la règle
> avec `audit2allow -w` avant de l'installer.

Un dernier mot sur `sealert`, souvent cité : il vient du paquet
`setroubleshoot-server`, absent ici comme de toute installation minimale, et
comme en examen.

```bash
rpm -q setroubleshoot-server
```

```text
package setroubleshoot-server is not installed
```

Savoir lire l'AVC brut n'est donc pas un pis-aller : c'est la compétence attendue.

**Le réflexe à garder**, devant un service qui échoue avec un « Permission
denied » que les droits Unix n'expliquent pas :

1. `getenforce` : SELinux applique-t-il quelque chose ?
2. `sudo ausearch -m avc --success no -ts recent`, avec `--input-logs` si vous
   n'avez pas de terminal : sortir les refus réellement appliqués.
3. Lire `permissive=` avant toute conclusion : `1` signifie journalisé, pas bloqué.
4. Lire l'opération et `tclass` : elles désignent la famille de correction.
5. Lire `scontext` et `tcontext` : le type du demandeur et celui de la cible.
6. Corriger la cause, et seulement en dernier recours envisager un module.

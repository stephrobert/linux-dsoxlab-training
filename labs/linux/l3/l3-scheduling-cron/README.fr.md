# Lab — planifier une tâche avec cron

## Rappel

[**cron sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/)

Une ligne cron commence par cinq champs de temps, `minute heure jour-du-mois
mois jour-de-semaine`, puis la commande. Les fichiers système (`/etc/crontab`
et `/etc/cron.d/`) intercalent un champ **utilisateur** entre les cinq champs et
la commande ; les crontabs utilisateur (`crontab -e`, `crontab -l`) n'en ont
pas. Un champ à `*` vaut « toutes les valeurs ». Le service `crond` doit
tourner.

## Le cours

Les exemples ci-dessous planifient un script `/usr/local/sbin/inventaire` pour
le compte `veille`, à la minute, dans `/var/tmp/atelier` : le challenge, lui,
vous demandera un autre script, un autre horaire et un autre emplacement. Le but
est d'apprendre la méthode et surtout de savoir **prouver** qu'une tâche tourne.
Toutes les sorties viennent d'une AlmaLinux 10 (paquet `cronie`).

### Le démon d'abord : sans lui, une crontab parfaite ne fait rien

C'est le premier réflexe, et il évite une heure de recherche dans la mauvaise
direction.

```bash
systemctl status crond      # RHEL, Alma, Rocky, Fedora
systemctl status cron       # Debian, Ubuntu
```

```text
● crond.service - Command Scheduler
     Loaded: loaded (/usr/lib/systemd/system/crond.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-07-22 13:30:02 UTC; 1h 41min ago
   Main PID: 1081 (crond)
```

Deux mots comptent : `running` (il tourne maintenant) et `enabled` (il
redémarrera au boot). Si l'un des deux manque, `sudo systemctl enable --now
crond`.

### Les trois emplacements, et comment les distinguer

| Emplacement | Champ utilisateur | Horaire propre | Qui écrit dedans |
|---|---|---|---|
| `crontab -e` → `/var/spool/cron/<user>` | non | oui, 5 champs | l'utilisateur |
| `/etc/crontab` et `/etc/cron.d/*` | **oui**, en 6e position | oui, 5 champs | root, les paquets |
| `/etc/cron.{hourly,daily,weekly,monthly}/` | non (root) | **non** | root, les paquets |

Une crontab utilisateur s'édite avec `crontab -e`, jamais en ouvrant le fichier
à la main. La commande valide la syntaxe avant d'installer, ce qu'un éditeur ne
ferait pas :

```bash
echo "* * * * /bin/true" | crontab -      # quatre champs de temps seulement
```

```text
"-":1: bad day-of-week
Invalid crontab file, can't install.
```

Elle vérifie aussi les bornes : `0 25 * * * /bin/true` donne `"-":1: bad hour`.
Le fichier réellement produit se trouve sous `/var/spool/cron/`, un fichier par
utilisateur, en `0600` :

```bash
sudo ls -l /var/spool/cron/
```

```text
-rw-------. 1 veille veille 162 Jul 22 15:11 veille
```

> Le guide annonce `/var/spool/cron/crontabs/` : c'est l'emplacement de Debian
> et Ubuntu. Sur cette AlmaLinux, le fichier est directement
> `/var/spool/cron/<utilisateur>`. Cherchez aux deux endroits.

Pour lire la table d'un autre compte, `crontab -l -u <utilisateur>` en root.
Les fichiers de `/etc/cron.d/` ont **six** champs, l'utilisateur venant avant la
commande, et rien n'oblige que ce soit root :

```text
# m h dom mon dow user command
* * * * * veille /usr/bin/id -un >> /var/tmp/atelier/systeme.log 2>&1
```

Enfin, `/etc/cron.hourly/` et consorts ne contiennent **pas** d'horaire : leurs
scripts sont lancés en bloc par un autre mécanisme. C'est
`/etc/cron.d/0hourly`, livré par le paquet, qui donne l'heure :

```text
01 * * * * root run-parts /etc/cron.hourly
```

### Voir la tâche s'exécuter : la seule preuve qui vaille

Déclarer une tâche ne prouve rien. On la programme **à la minute** le temps de
la vérifier, puis on remet le vrai horaire.

```bash
sudo useradd -m veille
sudo -u veille mkdir -p /var/tmp/atelier
sudo install -m 0755 /dev/stdin /usr/local/sbin/inventaire <<'EOF'
#!/bin/bash
echo "$(date +%H:%M:%S) inventaire lance" >> /var/tmp/atelier/battement.log
EOF
sudo -u veille crontab -e     # y écrire :  * * * * * /usr/local/sbin/inventaire
```

Deux minutes plus tard, la première preuve, le fichier témoin :

```bash
cat /var/tmp/atelier/battement.log
```

```text
15:12:01 inventaire lance
15:13:02 inventaire lance
15:14:01 inventaire lance
```

La seconde preuve, indépendante du script : le journal. Attention au filtre.

```bash
sudo journalctl _COMM=crond --since "-5min"
```

```text
crond[1081]: (veille) RELOAD (/var/spool/cron/veille)
CROND[22276]: (veille) CMD (/usr/local/sbin/inventaire)
CROND[22390]: (veille) CMDEND (/usr/local/sbin/inventaire)
```

`RELOAD` dit que le démon a vu la table changer, `CMD` qu'il a lancé la
commande, `CMDEND` qu'elle est terminée.

> Le guide propose `journalctl -u crond`. Sur cette machine, ce filtre ne
> retourne **aucune** ligne `CMD` : sur la même fenêtre de six minutes,
> `-u crond` en compte 0 et `_COMM=crond` en compte 29. Les exécutions sont
> attribuées à un `session-<n>.scope` et non à `crond.service` ; seuls les
> messages du démon lui-même (comme `BAD FILE MODE`) restent visibles avec
> `-u crond`. Utilisez `_COMM=crond`, ou le fichier `/var/log/cron` qui
> contient les mêmes lignes.

Une fois la preuve faite, on repasse à l'horaire voulu, par exemple
`15 4 * * 6` pour un samedi à 04:15.

### L'environnement de cron : le piège numéro un

Une tâche qui marche au clavier et pas dans cron, c'est presque toujours le
`PATH`. Faisons exécuter `env` **par cron** pour le mesurer, plutôt que de le
supposer :

```bash
# dans la crontab de veille
* * * * * /usr/bin/env > /var/tmp/atelier/env-cron.txt 2>&1
```

```text
HOME=/home/veille
LANG=en_US.UTF-8
LOGNAME=veille
PATH=/usr/bin:/bin:/usr/sbin:/sbin
PWD=/home/veille
SHELL=/bin/sh
USER=veille
```

Quatorze variables en tout, quelques `XDG_*` complétant la liste, contre une
vingtaine dans une session de connexion dont le `PATH` est bien plus long :

```text
/home/veille/.local/bin:/home/veille/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin
```

Trois différences à retenir :

- le `PATH` de cron ne contient **ni `/usr/local/bin` ni `/usr/local/sbin`**,
  là où atterrissent justement les scripts maison ;
- `SHELL` vaut `/bin/sh`, pas `/bin/bash` : les commodités de bash (`[[ ]]`,
  `source`) n'y sont pas garanties ;
- rien de ce que posent `/etc/profile` et `~/.bashrc` n'est là, ni `MAIL`,
  ni `HISTSIZE`, ni les variables de votre application.

La démonstration, avec la même commande écrite sans chemin absolu :

```bash
* * * * * inventaire >> /var/tmp/atelier/chemin-relatif.log 2>&1
```

```text
/bin/sh: line 1: inventaire: command not found
```

D'où la règle : **chemins absolus partout**. Si vous ne pouvez pas modifier le
script, déclarez les variables en tête de crontab, avant les lignes de tâches :

```text
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

### Où part la sortie quand personne ne la redirige

Une tâche cron n'a pas de terminal. Sa sortie part par courriel au destinataire
de `MAILTO` (`/etc/crontab` fixe `MAILTO=root` par défaut). Sur cette machine,
aucun agent de courrier n'est installé :

```bash
rpm -q postfix s-nail
```

```text
package postfix is not installed
package s-nail is not installed
```

La sortie ne disparaît pas pour autant : `cronie` la recopie dans le journal
sous l'étiquette `CMDOUT`. Avec la ligne `* * * * * /bin/echo "bilan pret"` :

```text
CROND[22872]: (veille) CMD (/bin/echo "bilan pret")
CROND[22857]: (veille) CMDOUT (bilan pret)
```

Mesuré : mettre `MAILTO=""` en tête de crontab **ne supprime pas** ces lignes
`CMDOUT`. `MAILTO` gouverne le courrier, pas la journalisation. Le seul moyen
de maîtriser la sortie est de la rediriger vous-même :
`>> /var/tmp/atelier/inventaire.log 2>&1` pour la garder, `> /dev/null 2>&1`
pour la jeter.

Dernier détail qui coûte cher : dans une crontab, `%` signifie « fin de
commande, la suite est l'entrée standard ». Comparez les deux lignes suivantes
et ce que le journal en fait.

```text
* * * * * /bin/date "+%F"  >> /var/tmp/atelier/pourcent-brut.log 2>&1
* * * * * /bin/date "+\%F" >> /var/tmp/atelier/pourcent-echappe.log 2>&1
```

```text
CROND[22742]: (veille) CMD (/bin/date "+)
CROND[22722]: (veille) CMDOUT (/bin/sh: -c: line 1: unexpected EOF while looking for matching `"')
CROND[22786]: (veille) CMD (/bin/date "+%F" >> /var/tmp/atelier/pourcent-echappe.log 2>&1)
```

La première ligne est tronquée au `%` : la redirection elle-même a disparu et
aucun fichier n'est créé. La seconde, échappée en `\%`, écrit bien son
`2026-07-22`. Échappez **tous** les `%`.

### Ce que cron refuse, et comment tout défaire

Trois fichiers déposés dans `/etc/cron.d/`, trois sorts différents, mesurés sur
trois minutes :

| Fichier | Droits | Résultat |
|---|---|---|
| `atelier-systeme` | `0644` | exécuté |
| `atelier.avec.point` | `0644` | **exécuté aussi** |
| `atelier-droits` | `0666` | jamais exécuté |

> Contrairement à une croyance répandue, `cronie` ne rejette **pas** un fichier
> de `/etc/cron.d/` dont le nom contient un point : `atelier.avec.point` a bien
> écrit ses trois lignes. En revanche, un fichier accessible en écriture au-delà
> de son propriétaire est écarté, et pas en silence :

```text
crond[1081]: (root) BAD FILE MODE (/etc/cron.d/atelier-droits)
```

C'est l'une des rares lignes que `journalctl -u crond` affiche. Les fichiers de
`/etc/cron.d/` se posent en `0644 root:root`.

Le tri des répertoires périodiques obéit, lui, à `run-parts`, et on peut le
demander sans attendre l'heure :

```bash
sudo run-parts --test /etc/cron.hourly
```

```text
/etc/cron.hourly/0anacron
/etc/cron.hourly/atelier-menage
/etc/cron.hourly/atelier-menage.sh
```

Un quatrième fichier, `atelier-non-exec` en `0644`, n'apparaît pas : **le bit
d'exécution est obligatoire**. Le `.sh`, en revanche, passe.

> Le guide écrit que `run-parts` ignore les fichiers dont le nom contient un
> point. Ce n'est pas vrai de la version livrée ici (paquet `crontabs`) : la
> lecture de `/usr/bin/run-parts` montre une liste fermée de suffixes écartés
> (`.rpmsave`, `.rpmorig`, `.rpmnew`, `.swp`, `.cfsaved`, `,v`, plus les noms
> finissant par `~` ou `,`). C'est la règle de Debian, pas celle-ci. Évitez
> quand même les extensions : elles ne sont portables nulle part.

Cron refuse aussi des personnes : `/etc/cron.allow` et `/etc/cron.deny`
filtrent l'accès à la commande `crontab`. Trois états mesurés avec `veille` :

| État des fichiers | `crontab -l` en tant que `veille` |
|---|---|
| `cron.deny` présent et vide, pas de `cron.allow` | affiche la table |
| aucun des deux | `You (veille) are not allowed to use this program` |
| `cron.allow` contenant seulement `root` | `You (veille) are not allowed to use this program` |

Le deuxième cas confirme la règle des distributions RHEL : sans aucun des deux
fichiers, seul root peut utiliser cron. Si AlmaLinux ouvre cron à tout le monde,
c'est qu'elle livre un `/etc/cron.deny` **vide**, à ne pas supprimer étourdiment.

Pour le ménage, `crontab -r` supprime toute la table sans confirmation, et le
`r` est voisin du `e` au clavier. `cronie` amortit la faute en gardant une
copie, ce que `sudo -u veille crontab -r` annonce lui-même :

```text
Backup of veille's previous crontab saved to /home/veille/.cache/crontab/crontab.bak
```

Ce filet n'existe pas partout : prenez l'habitude de
`crontab -l > ~/crontab-sauvegarde.txt` avant toute modification, et de
`crontab ~/crontab-sauvegarde.txt` pour restaurer. Le nettoyage complet de la
démonstration, et sa vérification :

```bash
sudo -u veille crontab -r
sudo rm -f /etc/cron.d/atelier-* /usr/local/sbin/inventaire
sudo rm -rf /var/tmp/atelier
sudo userdel -r veille
sudo crontab -l -u veille    # no crontab for veille
ls /etc/cron.d/              # 0hourly seulement
```

Une tâche oubliée qui tourne à la minute est le pire héritage à laisser sur un
serveur : ne sautez jamais ces deux dernières lignes.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| Rien ne se déclenche, aucune ligne `CMD` | `crond` arrêté, vérifier `systemctl status crond` |
| `journalctl -u crond` semble vide | mauvais filtre, utiliser `_COMM=crond` ou `/var/log/cron` |
| `Invalid crontab file, can't install.` | moins de cinq champs de temps, ou une valeur hors bornes |
| `command not found` dans le log de la tâche | `PATH` de cron réduit, mettre un chemin absolu |
| Le script marche au clavier, pas dans cron | variables du profil absentes, `SHELL=/bin/sh` |
| La commande est tronquée dans `CMD (...)` | un `%` non échappé, écrire `\%` |
| Un fichier de `/etc/cron.d/` est ignoré | droits trop larges, chercher `BAD FILE MODE` dans le journal |
| Un script de `/etc/cron.hourly/` ne tourne pas | bit d'exécution absent, vérifier avec `run-parts --test` |
| `You (…) are not allowed to use this program` | `/etc/cron.allow` ou `/etc/cron.deny` |
| Aucune trace de la sortie | ni redirection ni agent de courrier, regarder les lignes `CMDOUT` |

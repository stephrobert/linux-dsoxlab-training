# Lab — créer un service systemd

## Rappel

[**Services systemd sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/)

Une unit `.service` dans `/etc/systemd/system/` a des sections `[Unit]`,
`[Service]` (`Type=`, `ExecStart=`, `Restart=`) et `[Install]` (`WantedBy=`).
Après l'avoir écrite ou modifiée, lance `systemctl daemon-reload`. `enable` la
relie à une cible (persistance au boot) ; `start` la lance maintenant ;
`enable --now` fait les deux.

## Le cours

Les exemples ci-dessous montent un service nommé `horodateur`, autour du script
`/usr/local/bin/horodateur.sh` : le challenge, lui, vous demandera un autre
programme, un autre nom d'unité et d'autres vérifications. Le but est
d'apprendre la méthode et de savoir la déboguer, pas de recopier une ligne.
Toutes les sorties viennent d'AlmaLinux 10, **systemd 257**.

### Écrire l'unité et la charger

Il faut deux choses : un programme, et un fichier qui dit à systemd comment le
lancer. Le programme d'abord, avec le **bit d'exécution** (son absence est la
première cause d'échec) :

```bash
sudo tee /usr/local/bin/horodateur.sh >/dev/null <<'EOF'
#!/bin/bash
echo "horodateur demarre (PID $$)"
while true; do date +%T > /run/horodateur.tick; sleep 5; done
EOF
sudo chmod 0755 /usr/local/bin/horodateur.sh
```

L'unité ensuite, dans `/etc/systemd/system/`, le répertoire réservé à
l'administrateur. Trois blocs, trois questions : `[Unit]` décrit le service,
`[Service]` dit **comment lancer le processus**, `[Install]` **à quelle cible
le rattacher** au boot.

```bash
sudo tee /etc/systemd/system/horodateur.service >/dev/null <<'EOF'
[Unit]
Description=Horodateur de demonstration

[Service]
Type=simple
ExecStart=/usr/local/bin/horodateur.sh

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now horodateur.service
```

```text
Created symlink '/etc/systemd/system/multi-user.target.wants/horodateur.service' → '/etc/systemd/system/horodateur.service'.
```

Ce lien symbolique **est** l'activation au boot : `enable` ne fait rien d'autre
que le créer dans le `.wants` de la cible nommée par `WantedBy=`. `status`
confirme l'état réel :

```text
● horodateur.service - Horodateur de demonstration
     Loaded: loaded (/etc/systemd/system/horodateur.service; enabled; preset: disabled)
     Active: active (running) since Wed 2026-07-22 15:30:40 UTC; 2s ago
   Main PID: 1780 (horodateur.sh)
     CGroup: /system.slice/horodateur.service
             ├─1780 /bin/bash /usr/local/bin/horodateur.sh
             └─1782 sleep 5
```

Trois lignes portent tout : **Loaded** donne le fichier réellement chargé et
l'activation au boot, **Active** l'état courant, **CGroup** les processus
rattachés. `enabled` et `active` sont indépendants : l'un parle du prochain
démarrage, l'autre de maintenant.

### La mettre en défaut, puis la faire relever

Un service déclaré mais jamais mis en défaut n'a rien prouvé. On tue le
processus principal et on regarde :

```bash
sudo kill -9 $(systemctl show -p MainPID --value horodateur)
sleep 2 && systemctl is-active horodateur
```

```text
failed
```

```text
× horodateur.service - Horodateur de demonstration
     Active: failed (Result: signal) since Wed 2026-07-22 15:30:49 UTC; 2s ago
    Process: 1780 ExecStart=/usr/local/bin/horodateur.sh (code=killed, signal=KILL)
```

Le service est tombé et il y reste : le défaut `Restart=no` ne relance rien.
`journalctl -u horodateur.service` dit la même chose, en plus daté. On ajoute
donc la politique de redémarrage dans la section `[Service]` :

```ini
Restart=on-failure
RestartSec=2s
```

Et là, sans rien faire d'autre, `systemctl` vous prévient à **chaque**
commande :

```text
Warning: The unit file, source configuration file or drop-ins of horodateur.service changed on disk. Run 'systemctl daemon-reload' to reload units.
```

Ce n'est pas un détail cosmétique. Tant que le rechargement n'a pas eu lieu,
systemd travaille sur la version qu'il a en mémoire, et il le prouve :

```bash
sudo systemctl restart horodateur          # avertissement, puis redémarrage
systemctl show -p Restart --value horodateur
```

```text
no
```

Le fichier dit `on-failure`, systemd applique `no`. C'est ainsi qu'on perd une
heure à modifier un fichier « sans effet ». Après `sudo systemctl daemon-reload`,
la même commande répond enfin `on-failure`. Seconde tentative de meurtre, avec
le PID relevé avant et après :

```bash
sudo systemctl daemon-reload && sudo systemctl restart horodateur
systemctl show -p MainPID --value horodateur     # 1940
sudo kill -9 1940
sleep 4 && systemctl is-active horodateur && systemctl show -p MainPID --value horodateur
```

```text
active
1950
```

Le PID a changé : systemd a relancé le programme. Le journal raconte la
séquence, et c'est la ligne `Scheduled restart job` qu'il faut savoir
reconnaître :

```text
Jul 22 15:31:02 atelier systemd[1]: horodateur.service: Main process exited, code=killed, status=9/KILL
Jul 22 15:31:02 atelier systemd[1]: horodateur.service: Failed with result 'signal'.
Jul 22 15:31:04 atelier systemd[1]: horodateur.service: Scheduled restart job, restart counter is at 1.
Jul 22 15:31:04 atelier systemd[1]: Started horodateur.service - Horodateur de demonstration.
```

`Restart=on-failure` relance après un code de sortie non nul, un signal ou un
timeout ; `Restart=always` relance aussi après une sortie propre, ce qui masque
les configurations cassées.

### `Type=` : ce que systemd croit du démarrage

`Type=` ne change pas la façon de lancer le programme, il change la façon dont
systemd **décide que le service est démarré**. Un mauvais choix produit des
diagnostics faux.

| Type | Ce que systemd considère | Pour quoi |
|------|--------------------------|-----------|
| `simple` | Démarré dès le fork, sans attendre l'`exec()` | Défaut historique |
| `exec` | Démarré quand l'`exec()` a réussi | Le bon défaut pour un binaire au premier plan |
| `forking` | Démarré quand le processus père a rendu la main | Daemons traditionnels, avec `PIDFile=` |
| `oneshot` | Démarré quand la commande s'est terminée | Tâches ponctuelles |
| `notify` | Démarré quand le programme appelle `sd_notify()` | Applications conçues pour systemd |

Le piège le plus courant : un programme qui **passe en arrière-plan tout seul**.
Avec `Type=simple`, systemd suit le processus qu'il a lancé, celui-ci se
termine aussitôt, et systemd en conclut que le service est fini. Un script de
deux lignes (`/usr/bin/sleep 600 &` puis un `echo`) le démontre :

```text
○ demo-detache.service - Programme qui passe en arriere-plan
     Active: inactive (dead)

Jul 22 15:31:25 atelier detache.sh[2083]: fils lance en arriere-plan, PID 2085
Jul 22 15:31:25 atelier systemd[1]: demo-detache.service: Deactivated successfully.
```

Pire que « inactif » : le fils a été tué avec le reste du cgroup,
`pgrep -a "sleep 600"` ne renvoie **rien**. Le même fichier en `Type=forking`
(suivi d'un `daemon-reload`) donne le résultat attendu, systemd adoptant le
survivant comme processus principal :

```text
     Active: active (running) since Wed 2026-07-22 15:31:33 UTC; 2s ago
    Process: 2208 ExecStart=/usr/local/bin/detache.sh (code=exited, status=0/SUCCESS)
   Main PID: 2209 (sleep)
```

Second piège, symétrique : `RemainAfterExit=yes` n'a de sens qu'avec
`oneshot`. Une unité `Type=oneshot` qui prépare un répertoire retombe
`inactive (dead)` sitôt son travail fini, ce qui est correct mais illisible
dans un `list-units`. La directive lui fait garder l'état `active (exited)` :

```text
# Type=oneshot seul :               Active: inactive (dead)
# Type=oneshot + RemainAfterExit=yes :
     Active: active (exited) since Wed 2026-07-22 15:31:42 UTC; 22ms ago
    Process: 2349 ExecStart=/usr/bin/install -d -m 0755 /var/tmp/atelier-demo (code=exited, status=0/SUCCESS)
```

L'ajouter à un `Type=simple` n'aurait aucun sens : le processus est censé
rester vivant, il n'y a pas de « après la sortie ».

### Où vit l'unité : `/etc`, `/usr/lib`, et les drop-ins

Deux répertoires portent des unités, et ils n'ont pas le même statut :
`/usr/lib/systemd/system/` appartient aux **paquets** et se fait réécrire au
premier `dnf update` ; `/etc/systemd/system/` appartient à
l'**administrateur** et l'emporte. Deux fichiers du même nom, un dans chaque
répertoire, et `systemctl show -p Description --value demo-prio` tranche :

```text
# fichier seulement dans /usr/lib/ :  Version fournie par le paquet
# après ajout dans /etc/ :            Version posee par administrateur
```

D'où la règle : **on ne modifie jamais un fichier de `/usr/lib`**. Deux outils
font le travail à votre place. `systemctl edit --full <unité>` copie l'unité
complète dans `/etc/systemd/system/` et l'ouvre dans un éditeur. `systemctl
edit <unité>` sans `--full` crée un **drop-in**, un fragment qui ne contient
que les directives à changer :

```bash
sudo systemctl edit --drop-in=redemarrage.conf horodateur.service
```

```text
Successfully installed edited file '/etc/systemd/system/horodateur.service.d/redemarrage.conf'.
```

Le fragment vaut deux lignes (`[Service]` et `RestartSec=10s`), le reste de
l'unité continue de venir du fichier d'origine et suivra ses mises à jour.
`systemctl cat` affiche l'empilement fichier par fichier, et `status` signale
le drop-in :

```text
    Drop-In: /etc/systemd/system/horodateur.service.d
             └─redemarrage.conf
```

`systemctl show -p RestartUSec --value horodateur.service` répond `10s` : le
drop-in a bien écrasé le `RestartSec=2s` du fichier principal.

### Provoquer les erreurs pour apprendre à les lire

Trois fautes classiques, et ce que la machine en fait réellement. **Un
`ExecStart` relatif** est refusé au chargement, avant tout démarrage.
L'unité prend l'état `Loaded: bad-setting` et `systemctl start` renvoie 1 :

```text
/etc/systemd/system/demo-fautes.service:6: Neither a valid executable name nor an absolute path: ./horodateur.sh
demo-fautes.service: Unit configuration has fatal error, unit will not be started.
```

Nuance à connaître : un **nom simple sans slash** est accepté, lui.
`ExecStart=horodateur.sh` démarre sans broncher, parce que systemd le cherche
dans une liste fixe de répertoires (`man systemd.service` : « Searched
directories include `/usr/local/bin/`, `/usr/bin/` »). Ce qui est interdit,
c'est un chemin **relatif**, pas un nom nu. Écrivez tout de même le chemin
absolu : c'est sans ambiguïté.

**Une directive inconnue** n'empêche rien. Sur une faute de frappe
(`Restrt=on-failure`), systemd **ignore** la clé, le service démarre, et la
politique de redémarrage que vous croyez avoir posée n'existe pas.
L'avertissement part dans le journal du système à chaque `daemon-reload`, là où
personne ne le lit :

```text
Jul 22 15:31:48 atelier systemd[1]: /etc/systemd/system/demo-fautes.service:7: Unknown key 'Restrt' in section [Service], ignoring.
```

**Sans section `[Install]`**, `systemctl enable` ne crée **aucun lien** et
renvoie pourtant le code de retour **0** : un script qui teste `$?` croira
l'activation réussie. Seule l'explication affichée trahit le problème.

```text
The unit files have no installation config (WantedBy=, RequiredBy=, UpheldBy=,
Also=, or Alias= settings in the [Install] section, [...])
```

`systemctl is-enabled` répond alors `static`, et c'est la seule vérification
qui compte : jamais le code de retour d'`enable`.

Ces fautes s'attrapent **avant** le premier démarrage avec
`systemd-analyze verify <fichier>`, qui lit l'unité comme le ferait systemd et
va plus loin que la syntaxe (il vérifie que l'exécutable d'`ExecStart=`
existe) :

```text
demo-fautes.service: Command /usr/local/bin/absent.sh is not executable: No such file or directory
rc=1
```

Sur une unité saine, il n'affiche rien et renvoie 0. Attention aux degrés de
sévérité : chemin invalide et exécutable absent donnent `rc=1`, la clé inconnue
n'est que signalée, avec `rc=0`.

Ce dernier cas illustre le piège de `Type=simple` : avec un `ExecStart`
pointant vers un fichier absent, `systemctl start` renvoie **0** alors que le
service meurt aussitôt (`start rc=0`, puis `is-active` répond `failed`).

```text
Jul 22 15:32:42 atelier systemd[1]: demo-fautes.service: Main process exited, code=exited, status=203/EXEC
```

**203/EXEC** est le code d'échec le plus fréquent : binaire introuvable, non
exécutable, ou faute de frappe dans le chemin. Ne vous fiez jamais au code de
retour de `start` avec `Type=simple` : vérifiez l'état après coup avec
`sleep 3 && systemctl is-active <unité>`.

### Défaire proprement, et dépanner

Supprimer le fichier ne suffit pas : le lien d'activation et l'état `failed`
survivent.

```bash
sudo systemctl disable --now horodateur.service
sudo rm -f  /etc/systemd/system/horodateur.service
sudo rm -rf /etc/systemd/system/horodateur.service.d
sudo systemctl daemon-reload && sudo systemctl reset-failed
systemctl list-units --failed
```

`disable` retire le lien
(`Removed '/etc/systemd/system/multi-user.target.wants/horodateur.service'.`),
`daemon-reload` fait oublier l'unité, `reset-failed` efface les compteurs
d'échec. La preuve tient en une ligne : `0 loaded units listed.`

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| Modification du fichier sans effet | systemd garde sa version en mémoire | `systemctl daemon-reload`, puis `restart` |
| `start` réussit mais le service est mort | `Type=simple` ne vérifie pas l'`exec()` | `sleep 3 && systemctl is-active <unité>`, ou `Type=exec` |
| `failed` avec `203/EXEC` | Binaire absent ou non exécutable | `ls -l` sur le chemin d'`ExecStart=`, puis `chmod +x` |
| `inactive (dead)` juste après `start` | Le programme passe en arrière-plan | `Type=forking`, ou lancer le programme au premier plan |
| `enable` ne crée aucun lien | Pas de section `[Install]` | Ajouter `WantedBy=multi-user.target`, `daemon-reload`, réactiver |
| `Loaded: bad-setting` | Directive fatale, souvent un `ExecStart` relatif | `systemd-analyze verify <fichier>` |
| Une directive semble ignorée | Faute de frappe dans la clé | `journalctl -b \| grep "Unknown key"` |
| Le service tourne mais disparaît au reboot | Jamais activé | `systemctl enable <unité>` puis vérifier `is-enabled` |

Les autres codes de sortie (`217/USER`, `200/CHDIR`), le durcissement avec
`systemd-analyze security` et les targets sont traités dans le guide compagnon
en tête de page.

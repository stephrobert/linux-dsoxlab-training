# Lab — lancer un conteneur détaché avec Podman

## Rappel

[**Podman sur le guide compagnon**](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/)

`podman run -d --name <nom> <image> <cmd>` lance un conteneur détaché.
`podman ps` liste les conteneurs actifs ; `podman inspect -f '{{.State.Running}}'`
lit s'il tourne. `podman rm -f` le supprime.

## Le cours

Les exemples ci-dessous travaillent avec l'image `docker.io/library/alpine:3.21`
et des conteneurs nommés `horloge`, `ephemere` et `port-haut` : le challenge,
lui, demandera un autre nom et une autre image. Le but est d'apprendre le geste,
pas de recopier une ligne. Toutes les sorties viennent d'une VM **AlmaLinux
10.2** en **Podman 5.8.2**, utilisateur ordinaire d'**UID 1001**.

### Vérifier Podman, et savoir d'où viennent les images

Sur une AlmaLinux minimale, Podman n'est pas là. Le paquet tire avec lui `crun`
(le runtime OCI), `conmon` (le superviseur d'un conteneur), `netavark` et
`aardvark-dns` (le réseau) et `passt` (la pile réseau en espace utilisateur),
sans activer le moindre service :

```bash
command -v podman || sudo dnf -y install podman
podman --version          # podman version 5.8.2
```

Moins évident : **un nom d'image court n'est pas forcément un nom Docker Hub**.
La résolution est pilotée par `/etc/containers/registries.conf` :

```bash
grep -vE '^\s*#|^\s*$' /etc/containers/registries.conf
```

```text
unqualified-search-registries = ["registry.access.redhat.com", "registry.redhat.io", "docker.io"]
short-name-mode = "enforcing"
```

Sur une base RHEL, les registres Red Hat sont donc interrogés **avant** Docker
Hub. Certains noms très courants portent en plus un alias explicite, livré par
le paquet `containers-common` dans `registries.conf.d/000-shortnames.conf` :
c'est lui, et non la liste de recherche, qui a répondu à `podman pull alpine` :

```text
Resolved "alpine" as an alias (/etc/containers/registries.conf.d/000-shortnames.conf)
Trying to pull docker.io/library/alpine:latest...
```

D'où la règle : **écrivez l'image en entier, avec son tag**
(`docker.io/library/alpine:3.21`). Vous savez alors ce que vous tirez, et le
`:latest` implicite ne changera pas sous vos pieds.

### Rootless : ni démon, ni privilèges

C'est ce qui distingue Podman de Docker, et cela se constate plutôt que cela ne
s'affirme. Trois questions posées à la machine :

```bash
podman info --format 'Rootless: {{.Host.Security.Rootless}}'
podman info --format 'GraphRoot: {{.Store.GraphRoot}}'
pgrep -a podman ; echo "code retour pgrep = $?"
```

```text
Rootless: true
GraphRoot: /home/ansible/.local/share/containers/storage
code retour pgrep = 1
```

`pgrep` ne rend rien (code 1) : **aucun processus `podman` ne tourne en
permanence**. La CLI n'est pas un client qui parle à un démon, elle lance
elle-même le conteneur. Le stockage n'est pas partagé non plus : les images
vivent dans votre `$HOME`, jamais dans `/var/lib/containers`.

> Un service optionnel `podman.socket` existe pour les outils qui réclament
> l'API Docker. Il n'est pas actif par défaut : `systemctl is-active
> podman.socket` répond `inactive`, en système comme en `--user`.

Lançons un conteneur détaché qui produit quelque chose à lire :

```bash
podman run -d --name horloge docker.io/library/alpine:3.21 \
  sh -c 'while true; do date; sleep 5; done'
podman ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```text
NAMES       IMAGE                          STATUS
horloge     docker.io/library/alpine:3.21  Up 9 seconds
```

Le même conteneur, vu de deux côtés. **Dedans**, `podman top horloge user pid comm` :

```text
USER        PID         COMMAND
root        1           sh
root        5           sleep
```

**Sur l'hôte**, `ps -eo user,pid,args | grep -E 'while true|sleep 5'` :

```text
ansible     6016 sh -c while true; do date; sleep 5; done
ansible     6031 sleep 5
```

`root` en PID 1 côté conteneur, `ansible` côté hôte : c'est le même processus,
vu de deux espaces de noms, et il n'a jamais eu le moindre privilège. À côté de
lui tourne un `conmon`, à `ansible` lui aussi, qui tient les flux et le code de
sortie.

### Le décalage d'UID : subuid, subgid et les volumes

Comment être `root` dedans sans l'être dehors ? Par un *user namespace*, dont
les plages sont déclarées à la création du compte :

```bash
grep "^$USER:" /etc/subuid /etc/subgid
podman unshare cat /proc/self/uid_map
```

```text
/etc/subuid:ansible:589824:65536
/etc/subgid:ansible:589824:65536
         0       1001          1
         1     589824      65536
```

Lisez chaque ligne de `uid_map` de gauche à droite : *UID de départ dans le
conteneur*, *UID correspondant sur l'hôte*, *nombre d'UID*. Deux lignes, donc
deux règles :

| Dans le conteneur | Sur l'hôte | Pourquoi |
|---|---|---|
| `0` (root) | `1001` (vous) | votre propre UID, une seule valeur |
| `1` à `65536` | `589824` à `655359` | la plage réservée dans `/etc/subuid` |

Le vérifier sur un fichier vaut mieux qu'un schéma. On crée un volume, on y
écrit en tant que root **du conteneur**, puis on regarde le résultat depuis
l'hôte (`:Z` est la part SELinux : il demande le réétiquetage du contenu) :

```bash
podman volume create notes
podman run --rm -v notes:/data:Z docker.io/library/alpine:3.21 \
  sh -c 'echo bonjour > /data/note.txt; ls -ln /data'
ls -ln "$(podman volume inspect notes --format '{{.Mountpoint}}')"
```

```text
-rw-r--r--    1 0        0                8 Jul 22 15:49 note.txt   # dedans
-rw-r--r--. 1 1001 1001 8 Jul 22 15:49 note.txt                     # dehors
```

**UID 0 dedans, UID 1001 dehors : le fichier vous appartient.** Le même fichier
`chown 1000:1000` depuis le conteneur appartient ensuite, sur l'hôte, à `590823`
(`589824 + 1000 - 1`), qui ne correspond à aucun compte. C'est l'origine des
`permission denied` sur les dossiers partagés, que `--userns=keep-id` corrige.

### Les deux surprises du rootless

**Un port sous 1024 est refusé.** Le noyau les réserve à root, et vous ne l'êtes
pas :

```bash
podman run -d --name essai-port -p 80:8080 \
  docker.io/library/alpine:3.21 sleep 300
```

```text
Error: pasta failed with exit code 1:
Failed to bind port 80 (Permission denied) for option '-t 80-80:8080-8080'
```

Le message ne parle pas de Podman mais de **pasta**, le processus qui porte le
réseau rootless et ouvre réellement la socket sur l'hôte. Au-dessus de 1024,
tout se passe bien, et `ss` confirme qui écoute :

```bash
podman run -d --name port-haut -p 8080:8080 \
  docker.io/library/alpine:3.21 sleep 30
podman port port-haut ; ss -tlnp | grep 8080
```

```text
8080/tcp -> 0.0.0.0:8080
LISTEN 0  128  *:8080  [...]  users:(("pasta.avx2",pid=5753,fd=6))
```

Le seuil est le `sysctl net.ipv4.ip_unprivileged_port_start`, à `1024` ici : on
peut l'abaisser, mais publier sur un port haut reste le réflexe.

**Un conteneur rootless ne survit pas à votre déconnexion.** Vérifié en laissant
`horloge` tourner, puis en fermant toutes les sessions de l'utilisateur.
Observé depuis un autre compte, l'utilisateur passe en `closing`, puis disparaît
de `loginctl list-users` au bout d'une minute environ. Au retour,
`podman ps -a --format 'table {{.Names}}\t{{.Status}}'` :

```text
NAMES       STATUS
horloge     Exited (137)
```

`137` = `128 + 9`, donc `SIGKILL` : systemd a démonté `/run/user/1001` avec la
dernière session et emporté le conteneur. Le correctif tient en une commande :

```bash
loginctl enable-linger        # ou : sudo loginctl enable-linger <user>
loginctl list-users
```

L'essai refait avec le *linger* actif donne, après deux minutes sans aucune
session ouverte, un utilisateur en `lingering` (et non plus `closing` puis
disparu) et le processus du conteneur toujours vivant :

```text
 UID USER    LINGER STATE
1001 ansible yes    lingering
```

Sans `enable-linger`, un service rootless meurt avec votre `exit`.

### Le cycle de vie, de bout en bout

`podman ps` ne montre que les conteneurs **actifs** ; `podman ps -a` montre
aussi les morts, et c'est là que se cachent les surprises :

```bash
podman exec horloge cat /etc/alpine-release      # dans un conteneur vivant
podman logs --tail 3 horloge                     # la sortie standard du PID 1
podman run --rm docker.io/library/alpine:3.21 echo "conteneur jetable"
podman run -d --name ephemere docker.io/library/alpine:3.21 date
podman ps -a --format 'table {{.Names}}\t{{.Status}}'
```

```text
3.21.7
Wed Jul 22 15:54:30 UTC 2026
Wed Jul 22 15:54:35 UTC 2026
Wed Jul 22 15:54:40 UTC 2026
conteneur jetable
NAMES       STATUS
horloge     Up 2 minutes
ephemere    Exited (0) 2 seconds ago
```

Deux conteneurs lancés, un seul subsiste : `--rm` a fait disparaître le jetable
dès la fin de sa commande, alors que `ephemere` reste en `Exited (0)` parce que
sa commande (`date`) s'est terminée. **Un conteneur vit exactement le temps de
son processus principal** : c'est pourquoi un service détaché a besoin d'une
commande qui dure.

Un conteneur `Exited` occupe toujours son nom. Relancer `podman run -d --name
horloge ...` rend alors (message réel, raccourci) :

```text
Error: creating container storage: the container name "horloge" is already
in use by d1bd081db09315[...]. [...] use --replace to instruct Podman to do so.
```

L'arrêt et la suppression, enfin :

```bash
podman stop horloge
podman rm ephemere
```

```text
time="[...]" level=warning msg="StopSignal SIGTERM failed to stop container
horloge in 10 seconds, resorting to SIGKILL"
horloge
ephemere
```

`podman ps -a` affiche ensuite `horloge  Exited (137)` : `sh` ne relaie pas
`SIGTERM` à sa boucle, Podman attend dix secondes, puis tue. Un vrai service,
lui, sort en `0`.

### Images, espace disque, et ce qui reste quand on croit avoir tout supprimé

Les images se listent et se suppriment séparément des conteneurs, et une image
tenue par un conteneur, **même arrêté**, ne se supprime pas :

```bash
podman images
podman rmi docker.io/library/alpine:3.21
```

```text
REPOSITORY                 TAG         IMAGE ID      CREATED        SIZE
docker.io/library/alpine   3.21        2607caa98058  3 months ago   8.13 MB
[...]
Error: image used by d1bd081db093[...]: image is in use by a container:
consider listing external containers and force-removing image
```

Une fois tous les conteneurs retirés, il reste ce qu'on avait oublié :

```bash
podman rm -af && podman system df
```

```text
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         3           0           21.51MB     21.51MB (100%)
Containers     0           0           0B          0B (0%)
Local Volumes  1           0           8B          8B (100%)
```

`podman ps -a` est vide, et pourtant 21 Mo d'images et un volume dorment dans
`~/.local/share/containers` (`du -sh` y confirme les 21 Mo). C'est la colonne
**RECLAIMABLE** qu'il faut lire. D'où trois commandes pour nettoyer :

```bash
podman rm -af            # conteneurs, même actifs
podman rmi -af           # images  → Untagged: ... / Deleted: ...
podman volume prune -f   # volumes inutilisés → notes
```

et trois autres pour le prouver, pas une de moins :

```bash
podman ps -a --format 'table {{.Names}}\t{{.Status}}'
podman images ; podman system df
```

```text
NAMES       STATUS
REPOSITORY  TAG         IMAGE ID    CREATED     SIZE
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         0           0           0B          0B (0%)
Containers     0           0           0B          0B (0%)
Local Volumes  0           0           0B          0B (0%)
```

Trois en-têtes sans une seule ligne de données : il ne reste rien.
`podman system prune -a --volumes -f` fait tout cela d'un coup, mais supprime
sans discuter : sur une machine partagée, préférez les suppressions explicites.

> Sur Podman 6, `podman volume prune` ne retire plus que les volumes **anonymes**
> par défaut ; il faut `--all` pour retrouver le comportement montré ici. La VM
> de ce lab est en 5.8, la question ne se pose pas encore.

Réseaux, pods, Quadlet et construction d'images sont hors sujet ici : le
[guide compagnon](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/)
les traite chapitre par chapitre.

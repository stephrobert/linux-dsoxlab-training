# Lab — gérer les images de conteneurs avec podman & skopeo

## Rappel

[**Les images de conteneurs sur le guide compagnon**](https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/)

`podman pull <ref>` récupère une image depuis un registre ; `podman tag <src>
<nom>` lui donne un nom local ; `podman save -o <fichier> <nom>` écrit une archive
portable ; `skopeo inspect docker-archive:<fichier>` lit les métadonnées d'une
archive sans l'exécuter. `podman image exists <nom>` teste la présence.

## Le cours

Les exemples ci-dessous construisent une image `localhost/inventaire` à partir
de `registry.access.redhat.com/ubi9/ubi-minimal:9.6`, dans un répertoire
`~/atelier-image` : le challenge, lui, part d'une autre image et demande
d'autres gestes. Le but est de comprendre ce qu'est une image, pas de recopier
une ligne. Toutes les sorties viennent d'une VM **AlmaLinux 10.2** en **Podman
5.8.2**, sous un compte ordinaire (rootless).

Le mode rootless, le décalage d'UID et le cycle de vie des conteneurs sont
traités dans le lab `l4-podman-basic` : ici, on ne parle que d'images.

### Écrire un Containerfile et mesurer ce qu'il produit

Sur une AlmaLinux minimale, Podman n'est pas installé : `sudo dnf -y install
podman` tire 16 paquets (`crun`, `conmon`, `netavark`, `containers-common`…).
Second réflexe avant d'écrire quoi que ce soit : `/etc/containers/registries.conf`
interroge ici **les registres Red Hat avant Docker Hub**, en
`short-name-mode = "enforcing"`. Écrivez donc toujours vos images en entier,
registre et tag compris.

Un `Containerfile` est un fichier texte : une instruction par ligne, exécutées
dans l'ordre. `FROM` choisit l'image de base, `RUN` exécute une commande,
`COPY` verse un fichier du répertoire de construction dans l'image, `LABEL`
ajoute une métadonnée et `CMD` fixe la commande lancée par défaut.

```bash
mkdir ~/atelier-image && cd ~/atelier-image
printf 'ref;libelle\nA-100;vanne 3 pouces\nA-220;joint torique\n' > catalogue.txt
cat > Containerfile <<'EOF'
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6
LABEL org.opencontainers.image.title="inventaire"
RUN microdnf install -y findutils && microdnf clean all
COPY catalogue.txt /opt/inventaire/catalogue.txt
CMD ["cat", "/opt/inventaire/catalogue.txt"]
EOF
podman build -t localhost/inventaire:0.1 .
```

Le point (`.`) final n'est pas décoratif : c'est le **contexte de construction**,
le répertoire depuis lequel `COPY` a le droit de lire. La sortie annonce chaque
étape, et un identifiant après chacune :

```text
STEP 1/5: FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6
Trying to pull registry.access.redhat.com/ubi9/ubi-minimal:9.6...
[...]
STEP 3/5: RUN microdnf install -y findutils && microdnf clean all
[...]
--> 95fa94c7ade0
STEP 4/5: COPY catalogue.txt /opt/inventaire/catalogue.txt
--> c53008494027
STEP 5/5: CMD ["cat", "/opt/inventaire/catalogue.txt"]
COMMIT localhost/inventaire:0.1
--> bc5f1ccfccc4
```

Chaque `-->` est une image intermédiaire, réutilisable. Le résultat se mesure :

```text
REPOSITORY                                   TAG   IMAGE ID      SIZE
localhost/inventaire                         0.1   bc5f1ccfccc4  121 MB
registry.access.redhat.com/ubi9/ubi-minimal  9.6   a2c5a85865a5  106 MB
```

106 Mo de base, 121 Mo à l'arrivée : le paquet installé et le catalogue pèsent
15 Mo. Un `podman run --rm localhost/inventaire:0.1` affiche bien le catalogue,
sans qu'on ait à préciser la commande : c'est le `CMD`.

### Le cache de construction, et l'ordre qui le préserve

Relancez la même construction sans rien changer :

```text
STEP 3/5: RUN microdnf install -y findutils && microdnf clean all
--> Using cache 95fa94c7ade03223914ff23462af010347a5bcc79013a9fa5c91d61fa9da1be2
STEP 4/5: COPY catalogue.txt /opt/inventaire/catalogue.txt
--> Using cache c53008494027ad796e9f5ff8ed56b1c23617772e5102eb80f0e73ddc27b31613
```

`Using cache` à chaque étape, et **0,32 s** au lieu des 12,7 s de la première
fois, téléchargement de l'image de base compris. Ajoutez maintenant une ligne à
`catalogue.txt` et reconstruisez :

```text
STEP 3/5: RUN microdnf install -y findutils && microdnf clean all
--> Using cache 95fa94c7ade0[...]
STEP 4/5: COPY catalogue.txt /opt/inventaire/catalogue.txt
--> 196d41c74ed8
```

Le `RUN` reste en cache, le `COPY` est rejoué : Podman compare le contenu du
fichier copié, pas sa date. Et **tout ce qui suit une étape invalidée est
rejoué**, même si le texte de l'instruction n'a pas bougé.

D'où l'importance de l'ordre. Écrivons un second Containerfile identique, mais
avec le `COPY` placé **avant** le `RUN`. Une ligne ajoutée au catalogue, puis
les deux versions reconstruites l'une après l'autre, deux fois de suite :

| Ordre | 1re mesure | 2e mesure | Ce qui est rejoué |
|---|---|---|---|
| `RUN` puis `COPY` | 0,550 s | 0,619 s | `COPY` seulement |
| `COPY` puis `RUN` | 2,300 s | 2,480 s | `COPY` **et** l'installation |

Quatre fois plus lent pour un seul paquet de 563 ko. Avec un vrai jeu de
dépendances, l'écart se compte en minutes à chaque modification du code. La
règle tient en une phrase : **ce qui change rarement en haut, ce qui change
souvent en bas.**

### Lire une image : `podman history` et `podman inspect`

`podman history` déroule les instructions, de la dernière à la première, avec
ce que chacune a ajouté :

```bash
podman history --format 'table {{.Size}}\t{{.CreatedBy}}' localhost/inventaire:0.4
```

```text
SIZE        CREATED BY
0B          /bin/sh -c #(nop) CMD ["cat", "/opt/invent...
3.07kB      /bin/sh -c #(nop) COPY file:249809c51d33da...
14.9MB      /bin/sh -c microdnf install -y findutils &...
0B          /bin/sh -c #(nop) LABEL org.opencontainers...
106MB       /bin/sh -c #(nop) LABEL "architecture"="x8...
[...]
```

Trois lignes seulement pèsent quelque chose : 106 Mo pour la base, 14,9 Mo pour
l'installation, 3 ko pour le fichier copié. Total 121 Mo, ce que confirme
`podman inspect -f '{{.Size}}'` : `120954487`. Les `LABEL` et le `CMD` sont à
`0B` : ils ne touchent pas au système de fichiers, ils n'écrivent que des
métadonnées. La mention `#(nop)` signale d'ailleurs qu'aucune commande n'a
tourné.

Ne confondez pas nombre d'instructions et nombre de couches :
`podman history -q ... | wc -l` compte **23** lignes quand
`podman inspect -f '{{len .RootFS.Layers}}'` répond **3**. Seules `FROM`, `RUN`,
`COPY` et `ADD` créent une couche de fichiers.

Là où `history` raconte la fabrication, `inspect` donne l'état final. Sans
option il rend un JSON complet ; `-f` en extrait un champ, et c'est cette forme
qu'on utilise dans un script :

```bash
podman inspect -f '{{.Config.Cmd}}' localhost/inventaire:0.4
podman inspect -f '{{index .Config.Labels "org.opencontainers.image.title"}}' localhost/inventaire:0.4
podman inspect -f '{{.Architecture}}/{{.Os}}' localhost/inventaire:0.4
```

```text
[cat /opt/inventaire/catalogue.txt]
inventaire
amd64/linux
```

### Ce qui est écrit reste écrit

Voici le piège le plus coûteux du sujet. Deux Containerfile partant du même
`FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6` fabriquent un fichier de
40 Mio puis l'effacent, l'un en deux `RUN`, l'autre en un seul :

```dockerfile
# version « separee »
RUN dd if=/dev/urandom of=/opt/archive.bin bs=1M count=40 status=none
RUN rm -f /opt/archive.bin

# version « groupee »
RUN dd if=/dev/urandom of=/opt/archive.bin bs=1M count=40 status=none \
 && rm -f /opt/archive.bin
```

Dans les deux images, le fichier est bel et bien absent :

```text
$ podman run --rm localhost/purge:separee ls -l /opt/archive.bin
ls: cannot access '/opt/archive.bin': No such file or directory
```

Et pourtant :

```text
REPOSITORY:TAG                                   SIZE
localhost/purge:separee                          148 MB
localhost/purge:groupee                          106 MB
```

**42 Mo de différence pour un fichier que personne ne peut plus lire.** Le
`history` de la version en deux `RUN` le montre sans détour :

```text
SIZE        CREATED BY
2.05kB      /bin/sh -c rm -f /opt/archive.bin
41.9MB      /bin/sh -c dd if=/dev/urandom of=/opt/arch...
```

La couche du `rm` n'enregistre qu'une *suppression* ; la couche du dessous,
elle, contient toujours les 42 Mo. Une couche est immuable : on ne peut
qu'empiler par-dessus. D'où la règle : **on crée et on nettoie dans le même
`RUN`.**

Quand le fichier volumineux est indispensable à la fabrication mais inutile à
l'arrivée, la construction en plusieurs étapes règle le problème : un premier
`FROM` fait le travail sale, un second repart de zéro et ne copie que le
résultat.

```dockerfile
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6 AS travail
RUN dd if=/dev/urandom of=/opt/archive.bin bs=1M count=40 status=none
RUN sha256sum /opt/archive.bin > /opt/empreinte.txt

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6
COPY --from=travail /opt/empreinte.txt /opt/empreinte.txt
```

L'image finale pèse **106 Mo**, la taille de la base, et contient bien
l'empreinte calculée sur les 42 Mo. Le guide compagnon détaille cette technique
et les autres façons d'alléger une image.

### Étiqueter : `podman tag`, `latest` et les images `<none>`

`podman tag` ne copie rien du tout : il ajoute un nom qui pointe sur la même
image.

```bash
podman tag localhost/inventaire:0.4 localhost/inventaire:latest
podman tag localhost/inventaire:0.4 registry.exemple.lan/atelier/inventaire:stable
```

```text
REPOSITORY                               TAG      IMAGE ID      SIZE
registry.exemple.lan/atelier/inventaire  stable   0fb0af1ab155  121 MB
localhost/inventaire                     latest   0fb0af1ab155  121 MB
localhost/inventaire                     0.4      0fb0af1ab155  121 MB
```

**Trois lignes, un seul `IMAGE ID`, et trois fois 121 Mo affichés.** La colonne
`SIZE` n'est donc pas additionnable : à cet instant, sept noms affichaient
121 Mo chacun, soit 847 Mo si on les additionnait, quand `podman system df`
annonçait **222,6 Mo** pour l'ensemble du magasin. Les couches communes ne sont
stockées qu'une fois. `podman rmi` sur l'un des noms ne supprime que le nom :

```text
Untagged: registry.exemple.lan/atelier/inventaire:stable
```

Le préfixe compte : `localhost/` désigne une image locale, jamais publiée ;
`registry.exemple.lan/atelier/…` est le nom qu'il faudra pour un `podman push`.
Quant à `latest`, ce n'est **pas** « la dernière version », juste le tag
implicite quand on n'en précise aucun. La preuve sur la machine, après avoir
reconstruit `0.4` sans retoucher `latest` :

```text
REPOSITORY            TAG      IMAGE ID      CREATED
localhost/inventaire  0.4      09f03c2f59f3  17 seconds ago
localhost/inventaire  latest   0fb0af1ab155  49 seconds ago
```

`latest` est plus **vieux** que `0.4`. Rien ne le met à jour tout seul.

Et l'image qui portait `0.4` avant la reconstruction ? Elle n'a pas disparu :
elle a perdu son nom.

```text
$ podman images --filter dangling=true --format 'table {{.ID}}\t{{.Size}}'
IMAGE ID      SIZE
d756ef94e0c4  148 MB
bc5f1ccfccc4  121 MB
[...]
```

Ce sont les images `<none>` de `podman images`, dites *dangling*. Elles
occupent le disque comme les autres : ici, `podman image prune -f` en a retiré
quatorze et fait tomber le magasin de **222,7 Mo à 178 Mo**.

### Ce qui reste sur le disque

`podman system df` est la seule vue honnête de l'occupation. Avec un conteneur
en train d'écrire 20 Mo dans son système de fichiers :

```text
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         20          1           178MB       178MB (100%)
Containers     1           1           20.98MB     0B (0%)
```

Le conteneur possède sa propre couche inscriptible, comptée à part de l'image.
Tant qu'il existe, l'image lui reste attachée :

```text
Error: image used by 8ee48969ad21[...]: image is in use by a container:
consider listing external containers and force-removing image
```

Supprimez le conteneur : la ligne `Containers` retombe à `0B`, sa couche de
20,98 Mo part avec lui, **mais les 178 Mo d'images restent inchangés**.
Supprimer un conteneur ne libère jamais l'image dont il est issu, il la libère
seulement de son emprise.

Restent deux nettoyages à ne pas confondre :

| Commande | Ce qu'elle supprime |
|---|---|
| `podman image prune -f` | les seules images **sans nom** (`<none>`) |
| `podman image prune -a -f` | **toutes** les images qu'aucun conteneur n'utilise |

Sur l'état ci-dessus, `prune -f` ne rend plus rien (il n'y a plus de `<none>`)
alors que `prune -a -f` supprime les vingt images : `podman images` n'affiche
plus que son en-tête et `podman system df` tombe à `0B` partout. Le disque
suit, et c'est la vérification qui compte : mesuré à part sur trois images
construites depuis un magasin vide, `du -sh ~/.local/share/containers` donne
**158 Mo** avant, **300 ko** après le `prune -a -f`.
`podman system prune -a -f` fait la même chose pour les conteneurs, images et
réseaux d'un coup, mais sans rien demander : sur une machine partagée, préférez
les suppressions explicites.

### Dépannage

**`short-name resolution enforced but cannot prompt without a TTY`** : un `FROM`
en nom court que Podman ne sait pas résoudre seul. Écrivez le nom complet,
registre et tag compris.

**`possible escaping context directory error`** : un `COPY ../fichier` ne
fonctionnera jamais. `COPY` ne lit que sous le contexte de construction, le
répertoire passé en dernier argument de `podman build`.

**`no Containerfile or Dockerfile specified or found in context directory`** :
vous construisez depuis le mauvais répertoire, ou votre fichier porte un autre
nom. Dans ce cas, désignez-le : `podman build -f mon-fichier -t nom:tag .`

**`unable to delete image "..." by ID with more than one tag [...]: please force
removal`** : l'image porte plusieurs noms. Retirez-les un par un avec
`podman rmi <nom>:<tag>`, ou forcez avec `podman rmi -f`.

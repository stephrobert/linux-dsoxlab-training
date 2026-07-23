# Lab — liens physiques et symboliques

## Rappel

[**Naviguer dans les fichiers sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/)

Un **lien physique** (`ln cible nom`) est un autre nom pour le même inode : mêmes
données, compteur de liens qui augmente, et il survit à la suppression de
l'original. Un **lien symbolique** (`ln -s cible nom`) stocke un chemin vers la
cible ; il peut traverser les systèmes de fichiers et pointer un répertoire, mais
casse si la cible bouge. `ls -li` révèle l'inode et le compteur de liens.

## Le cours

Les exemples ci-dessous travaillent dans `~/atelier-liens`, sur un fichier
`rapport.log` et un répertoire `stock/archives` : le challenge, lui, vous
demandera d'autres noms dans un autre répertoire. Le but est d'apprendre à
observer, pas de recopier une ligne.

Toutes les sorties de cette page ont été relevées sur une AlmaLinux 10
(`coreutils 9.5`, système de fichiers **XFS**). Les numéros d'inode changeront
chez vous : ce qui compte, c'est qu'ils soient **égaux** ou **différents** là où
le texte le dit.

### Le décor de démonstration

```bash
mkdir -p ~/atelier-liens
cd ~/atelier-liens
printf "ligne 1 du rapport\nligne 2 du rapport\n" > rapport.log
ls -li
```

```text
total 4
309333 -rw-r--r--. 1 ansible ansible 38 Jul 22 13:58 rapport.log
```

L'option **`-i`** de `ls` ajoute une première colonne : le **numéro d'inode**.
C'est le vrai identifiant du fichier sur le système de fichiers. Le nom
`rapport.log`, lui, n'est qu'une entrée de répertoire qui pointe vers cet inode.

La colonne juste après les permissions (`1` ici) est le **nombre de liens**,
comme le rappelle la légende de `ls -l` dans le guide. Retenez ces deux
colonnes : tout ce lab tient dedans.

### Un lien physique : un second nom pour le même inode

```bash
ln rapport.log journal-dur.log
ls -li
```

```text
total 8
309333 -rw-r--r--. 2 ansible ansible 38 Jul 22 13:58 journal-dur.log
309333 -rw-r--r--. 2 ansible ansible 38 Jul 22 13:58 rapport.log
```

Deux lignes, **un seul numéro d'inode** : `309333` des deux côtés. Et le
compteur est passé de `1` à `2`. Il n'y a pas eu de copie : il y a maintenant
deux noms qui désignent le même fichier. `stat` le dit encore plus clairement :

```bash
stat rapport.log journal-dur.log
```

```text
  File: rapport.log
  Size: 38        	Blocks: 8          IO Block: 4096   regular file
Device: 252,4	Inode: 309333      Links: 2
Access: (0644/-rw-r--r--)  Uid: ( 1001/ ansible)   Gid: ( 1001/ ansible)
...
  File: journal-dur.log
  Size: 38        	Blocks: 8          IO Block: 4096   regular file
Device: 252,4	Inode: 309333      Links: 2
Access: (0644/-rw-r--r--)  Uid: ( 1001/ ansible)   Gid: ( 1001/ ansible)
```

Même `Device`, même `Inode`, même `Links`, mêmes permissions, même propriétaire.
Seul le champ `File` diffère, parce que c'est le seul qui ne soit pas stocké
dans l'inode.

Conséquence directe : ce qu'on écrit par un nom se lit par l'autre, et ce qu'on
change par un nom change pour l'autre.

```bash
echo "ligne 3 ajoutee par le lien" >> journal-dur.log
cat rapport.log
```

```text
ligne 1 du rapport
ligne 2 du rapport
ligne 3 ajoutee par le lien
```

```bash
chmod 640 journal-dur.log
ls -l rapport.log journal-dur.log
```

```text
-rw-r-----. 2 ansible ansible 66 Jul 22 13:58 journal-dur.log
-rw-r-----. 2 ansible ansible 66 Jul 22 13:58 rapport.log
```

Le `chmod` n'a été demandé que sur un nom, et les deux ont changé : les
permissions vivent dans l'inode, pas dans le nom.

### Le compteur de liens, et la survie des données

Supprimer un nom ne supprime pas le fichier : cela **décrémente** le compteur.
Le contenu n'est libéré que lorsque le compteur tombe à zéro.

```bash
rm rapport.log
ls -li
cat journal-dur.log
```

```text
total 4
309333 -rw-r-----. 1 ansible ansible 66 Jul 22 13:58 journal-dur.log
ligne 1 du rapport
ligne 2 du rapport
ligne 3 ajoutee par le lien
```

Le nom d'origine a disparu, l'inode `309333` est toujours là avec ses trois
lignes, et le compteur est redescendu à `1`. C'est la propriété qui distingue
vraiment un lien physique d'un simple pointeur : il n'y a pas de nom principal
et de nom secondaire, il y a **deux noms de rang strictement égal**.

On peut d'ailleurs refaire le nom perdu depuis le nom survivant, puis retirer
l'autre :

```bash
ln journal-dur.log rapport.log
ls -li
```

```text
total 8
309333 -rw-r-----. 2 ansible ansible 66 Jul 22 13:58 journal-dur.log
309333 -rw-r-----. 2 ansible ansible 66 Jul 22 13:58 rapport.log
```

```bash
rm journal-dur.log
ls -li
```

```text
total 4
309333 -rw-r-----. 1 ansible ansible 66 Jul 22 13:58 rapport.log
```

Le compteur monte, descend, et l'inode ne bouge pas.

### Le lien symbolique : un chemin, pas un inode

```bash
ln -s rapport.log courant.log
ls -li
```

```text
total 4
309334 lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
309333 -rw-r-----. 1 ansible ansible 66 Jul 22 13:58 rapport.log
```

Quatre différences sautent aux yeux par rapport au lien physique :

1. **inode différent** (`309334` contre `309333`) : c'est un fichier à part
   entière, d'un type à part entière ;
2. le premier caractère de la ligne est **`l`** et non `-` : le type du fichier
   est « lien symbolique » ;
3. les permissions affichées sont `rwxrwxrwx`, toujours, pour tout le monde ;
4. `ls -l` affiche la **cible** après une flèche, et la **taille est 11**, alors
   que le fichier visé en fait 66.

Onze, c'est exactement le nombre de caractères de la chaîne `rapport.log`. Un
lien symbolique ne contient rien d'autre que ce texte :

```bash
ln -s /home/ansible/atelier-liens/rapport.log absolu.log
ls -l courant.log absolu.log
```

```text
lrwxrwxrwx. 1 ansible ansible 39 Jul 22 13:58 absolu.log -> /home/ansible/atelier-liens/rapport.log
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
```

39 caractères pour `/home/ansible/atelier-liens/rapport.log`, 11 pour
`rapport.log`. La taille d'un lien symbolique **est** la longueur du chemin
qu'il stocke.

Pour lire ce chemin sans passer par `ls`, deux commandes complémentaires :

```bash
readlink courant.log        # le chemin tel qu'il est stocké
readlink -f courant.log     # le chemin final, une fois tout résolu
```

```text
rapport.log
/home/ansible/atelier-liens/rapport.log
```

Et pour voir des deux côtés du lien, `stat` sans puis avec `-L` :

```bash
stat -c  "%N | type=%F | taille=%s | inode=%i" courant.log
stat -Lc "%N | type=%F | taille=%s | inode=%i" courant.log
```

```text
'courant.log' -> 'rapport.log' | type=symbolic link | taille=11 | inode=309334
'courant.log' | type=regular file | taille=66 | inode=309333
```

Sans `-L`, `stat` décrit le **lien**. Avec `-L`, il décrit la **cible**. La
plupart des commandes (`cat`, `cp`, `grep`, `chmod`) suivent le lien par défaut,
comme `stat -L`.

Justement, les `rwxrwxrwx` du lien ne servent à rien : ce sont les droits de la
cible qui décident.

```bash
chmod 600 courant.log
ls -l courant.log rapport.log
```

```text
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
-rw-------. 1 ansible ansible 66 Jul 22 13:58 rapport.log
```

Le `chmod` a traversé le lien et modifié `rapport.log`, le lien n'a pas bougé.
Et `chmod -h`, qui existe pour viser le lien lui-même, ne change rien non plus
sous Linux : il sort en succès sans effet.

```bash
chmod -h 777 courant.log ; echo "rc=$?"
ls -l courant.log
```

```text
rc=0
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
```

Ne cherchez donc pas à « sécuriser » un lien symbolique par ses permissions :
elles sont décoratives.

### Le lien pendant, et comment le repérer

Puisque le lien ne contient qu'un chemin, il suffit que ce chemin cesse d'être
valide pour que le lien pointe dans le vide. C'est le **lien pendant**.

```bash
mv rapport.log rapport-2026.log
ls -l
```

```text
total 4
lrwxrwxrwx. 1 ansible ansible 39 Jul 22 13:58 absolu.log -> /home/ansible/atelier-liens/rapport.log
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
-rw-------. 1 ansible ansible 66 Jul 22 13:58 rapport-2026.log
```

Rien dans cette sortie ne signale la rupture : les deux liens affichent encore
fièrement leur cible. C'est à l'usage qu'elle apparaît :

```bash
cat courant.log ; echo "rc=$?"
```

```text
cat: courant.log: No such file or directory
rc=1
```

Le message est trompeur : ce n'est pas `courant.log` qui manque, c'est sa cible.
Les tests du shell font bien la différence :

```bash
test -e courant.log && echo "-e vrai" || echo "-e faux"
test -L courant.log && echo "-L vrai" || echo "-L faux"
```

```text
-e faux
-L vrai
```

**`-e`** teste ce qui est **au bout** du lien, **`-L`** teste le lien lui-même.
Un fichier peut donc être à la fois « inexistant » et « présent ».

Pour balayer une arborescence, `find` a l'option qu'il faut :

```bash
find . -type l                       # tous les liens symboliques
find . -xtype l                      # seulement ceux qui pendent
find . -xtype l -printf "%p -> %l\n" # avec le chemin qu'ils stockent
```

```text
./courant.log
./absolu.log
./courant.log -> rapport.log
./absolu.log -> /home/ansible/atelier-liens/rapport.log
```

`-xtype l` est la commande à retenir pour l'audit : elle ne remonte que les
liens cassés. Une fois la cible remise en place, elle n'affiche plus rien :

```bash
mv rapport-2026.log rapport.log
find . -xtype l
```

```text
```

### Relatif ou absolu : ce qui casse, et quand

Un lien relatif est interprété **depuis le répertoire où se trouve le lien**,
pas depuis celui d'où vous lancez la commande. Déplacer le lien suffit donc à le
casser, alors qu'un lien absolu survit.

```bash
mkdir -p sous-dossier
mv courant.log absolu.log sous-dossier/
cd sous-dossier
ls -l
```

```text
total 0
lrwxrwxrwx. 1 ansible ansible 39 Jul 22 13:58 absolu.log -> /home/ansible/atelier-liens/rapport.log
lrwxrwxrwx. 1 ansible ansible 11 Jul 22 13:58 courant.log -> rapport.log
```

```bash
cat courant.log  >/dev/null ; echo "courant rc=$?"
cat absolu.log   >/dev/null ; echo "absolu  rc=$?"
```

```text
cat: courant.log: No such file or directory
courant rc=1
absolu  rc=0
```

Chacun a son domaine :

- le lien **relatif** survit au déplacement de **l'ensemble** (lien et cible
  ensemble, une arborescence qu'on recopie ailleurs, un point de montage qui
  change) ;
- le lien **absolu** survit au déplacement du **lien seul**, mais casse si toute
  l'arborescence est remontée ailleurs.

### Les limites du lien physique

C'est ici que les deux outils cessent d'être interchangeables. Un lien physique
est une entrée de répertoire qui pointe un inode : il ne peut donc exister que
là où cet inode est adressable.

**Première limite : pas de lien physique vers un répertoire.**

```bash
mkdir -p stock/archives
ln stock/archives archives-dur ; echo "rc=$?"
sudo ln stock/archives archives-dur ; echo "rc=$?"
```

```text
ln: stock/archives: hard link not allowed for directory
rc=1
ln: stock/archives: hard link not allowed for directory
rc=1
```

Le refus vient du noyau, et `sudo` n'y change rien. La raison se voit dans le
compteur de liens d'un répertoire, qui est déjà utilisé par le système :

```bash
mkdir -p stock/archives/2025 stock/archives/2026
stat -c "%n : %h liens, inode %i" stock/archives stock/archives/. stock/archives/2025/..
```

```text
stock/archives : 4 liens, inode 25672520
stock/archives/. : 4 liens, inode 25672520
stock/archives/2025/.. : 4 liens, inode 25672520
```

Un même inode, trois chemins. Un répertoire a **2 liens de base** (son nom dans
le parent, et son propre `.`), **plus un par sous-répertoire** (le `..` de
chacun) : ici 2 + 2 = 4. Autoriser des liens physiques arbitraires vers des
répertoires permettrait de fabriquer des boucles dont aucun parcours ne
sortirait.

**Deuxième limite : pas de lien physique entre deux systèmes de fichiers.** Un
numéro d'inode n'a de sens qu'à l'intérieur d'un système de fichiers ; deux
fichiers sans rapport, sur deux disques, peuvent parfaitement porter le même
numéro.

> Les commandes qui suivent **effacent** le contenu de `/dev/vdb`. Vérifiez avec
> `lsblk` que ce disque est bien vide et sans point de montage avant de les
> lancer.

```bash
sudo mkfs.xfs -q -L ANNEXE /dev/vdb
sudo mkdir -p /mnt/annexe
sudo mount /dev/vdb /mnt/annexe
sudo chown "$USER":"$USER" /mnt/annexe
df -hT /mnt/annexe /
```

```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/vdb       xfs   2.0G   71M  1.9G   4% /mnt/annexe
/dev/vda4      xfs   8.8G  1.1G  7.7G  13% /
```

Deux systèmes de fichiers montés, chacun avec sa propre table d'inodes. La
tentative de lien physique de l'un vers l'autre échoue, avec un message qu'il
faut savoir reconnaître :

```bash
cd ~/atelier-liens
ln rapport.log /mnt/annexe/rapport-dur.log ; echo "rc=$?"
```

```text
ln: failed to create hard link '/mnt/annexe/rapport-dur.log' => 'rapport.log': Invalid cross-device link
rc=1
```

**`Invalid cross-device link`** : la traduction exacte de « ces deux chemins ne
sont pas sur le même système de fichiers ». Le lien symbolique, lui, passe sans
broncher, puisqu'il ne stocke qu'un texte :

```bash
ln -s /home/ansible/atelier-liens/rapport.log /mnt/annexe/rapport-lien.log
cat /mnt/annexe/rapport-lien.log
```

```text
ligne 1 du rapport
ligne 2 du rapport
ligne 3 ajoutee par le lien
```

Le mot « device » du message renvoie à un numéro que `stat` affiche :

```bash
cp ~/atelier-liens/rapport.log /mnt/annexe/rapport-copie.log
stat -c "%n : device %D, inode %i, liens %h" ~/atelier-liens/rapport.log /mnt/annexe/rapport-copie.log
```

```text
/home/ansible/atelier-liens/rapport.log : device fc04, inode 309333, liens 1
/mnt/annexe/rapport-copie.log : device fc10, inode 132, liens 1
```

Deux `device` différents : aucun lien physique n'est possible entre ces deux
fichiers. La même frontière explique le comportement de `mv`, qui se contente
de renommer une entrée de répertoire tant qu'il reste sur place, et doit copier
puis supprimer dès qu'il en sort :

```bash
echo x > f.txt ; stat -c "avant    : inode %i" f.txt
mv f.txt g.txt ; stat -c "meme fs  : inode %i" g.txt
mv g.txt /mnt/annexe/h.txt ; stat -c "autre fs : inode %i" /mnt/annexe/h.txt
```

```text
avant    : inode 17458674
meme fs  : inode 17458674
autre fs : inode 134
```

Le renommage garde l'inode, la traversée en fabrique un neuf.

**Troisième limite, moins connue : le noyau protège les liens physiques.** Sur
une distribution moderne, on ne peut pas créer de lien physique vers un fichier
dont on n'est ni propriétaire ni autorisé à écrire.

```bash
sysctl fs.protected_hardlinks fs.protected_symlinks
ln /etc/hostname /tmp/hostname-dur ; echo "rc=$?"
```

```text
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
ln: failed to create hard link '/tmp/hostname-dur' => '/etc/hostname': Operation not permitted
rc=1
```

`Operation not permitted` sur un `ln` alors que le répertoire de destination est
accessible en écriture : pensez à ce réglage avant de chercher ailleurs.

**Enfin, un lien physique exige que la cible existe déjà**, alors qu'un lien
symbolique se moque de savoir si la sienne existe :

```bash
ln absent.log copie.log ; echo "rc=$?"
ln -s absent.log futur.log ; echo "rc=$?"
ls -l futur.log
```

```text
ln: failed to access 'absent.log': No such file or directory
rc=1
rc=0
lrwxrwxrwx. 1 ansible ansible 10 Jul 22 13:59 futur.log -> absent.log
```

C'est utile : on peut poser un lien vers un fichier qui sera produit plus tard,
mais c'est aussi comme cela qu'on fabrique un lien pendant sans s'en rendre
compte, en se trompant d'un caractère dans le nom de la cible.

### Un lien symbolique vers un répertoire

Le lien symbolique n'a aucune des trois limites précédentes. En particulier, il
pointe très bien un répertoire :

```bash
echo "sauvegarde du 22" > stock/archives/backup-22.txt
ln -s stock/archives dernier
ls -l dernier
```

```text
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 13:59 dernier -> stock/archives
```

À partir de là, `dernier` s'utilise comme le répertoire visé. Attention toutefois
au comportement de `ls`, qui dépend de la présence d'une **barre oblique
finale** :

```bash
ls dernier          # liste le contenu
ls -l dernier       # decrit le lien
ls -l dernier/      # liste le contenu, format long
```

```text
2025
2026
backup-22.txt
```

```text
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 13:59 dernier -> stock/archives
```

```text
total 4
drwxr-xr-x. 2 ansible ansible  6 Jul 22 13:59 2025
drwxr-xr-x. 2 ansible ansible  6 Jul 22 13:59 2026
-rw-r--r--. 1 ansible ansible 17 Jul 22 13:59 backup-22.txt
```

La règle : **la barre oblique finale force la traversée du lien**. `dernier`
désigne le lien, `dernier/` désigne le répertoire au bout. Cette distinction
reviendra plus bas, et là elle fera des dégâts.

Le shell, lui, garde en mémoire le chemin par lequel vous êtes passé :

```bash
cd dernier
pwd        # chemin logique, celui que vous avez tape
pwd -P     # chemin physique, apres resolution des liens
cd ..
pwd
```

```text
/home/ansible/atelier-liens/dernier
/home/ansible/atelier-liens/stock/archives
/home/ansible/atelier-liens
```

Le `cd ..` n'a pas remonté vers `stock`, le parent réel, mais vers
`~/atelier-liens`, le parent du **lien**. C'est le comportement par défaut de
`cd`, et c'est une source d'erreurs quand on enchaîne des commandes relatives.
`cd -P` demande la traversée immédiate :

```bash
cd ~/atelier-liens
cd -P dernier
pwd
cd ..
pwd
```

```text
/home/ansible/atelier-liens/stock/archives
/home/ansible/atelier-liens/stock
```

Cette fois `cd ..` remonte bien dans `stock`.

### Remplacer un lien symbolique sans se faire piéger

Repointer un lien vers une autre cible est l'usage le plus courant du lien
symbolique (`dernier` qui suit la dernière sauvegarde, par exemple). C'est aussi
le geste qui piège le plus, dès que le lien vise un répertoire.

L'expérience qui suit a été menée dans un répertoire neuf, pour que les sorties
restent lisibles :

```bash
mkdir -p /tmp/essai/stock/archives /tmp/essai/stock/archives-2025
cd /tmp/essai
ln -s stock/archives dernier
ls -l
```

```text
total 0
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 14:00 dernier -> stock/archives
drwxr-xr-x. 4 ansible ansible 43 Jul 22 14:00 stock
```

Maintenant, repointons `dernier` vers `stock/archives-2025` avec le `-f`
habituel :

```bash
ln -sf stock/archives-2025 dernier ; echo "rc=$?"
ls -l dernier
```

```text
rc=0
lrwxrwxrwx. 1 ansible ansible 14 Jul 22 14:00 dernier -> stock/archives
```

Succès annoncé, et pourtant `dernier` pointe toujours au même endroit. Où est
passée la demande ?

```bash
ls -l stock/archives
```

```text
total 0
lrwxrwxrwx. 1 ansible ansible 19 Jul 22 14:00 archives-2025 -> stock/archives-2025
```

`ln` a traversé le lien, considéré `dernier` comme le répertoire de destination,
et créé un nouveau lien **dedans**. Le `-f` n'a servi qu'à autoriser
l'écrasement de ce lien intérieur. Le résultat est doublement mauvais : le lien
attendu n'a pas bougé, et un lien parasite, pendant de surcroît, est apparu dans
l'arborescence.

L'option qui corrige cela est **`-n`** (`--no-dereference`) : elle demande à
traiter une destination qui est un lien vers un répertoire comme un fichier
ordinaire.

```bash
rm -f stock/archives/archives-2025
ln -sfn stock/archives-2025 dernier ; echo "rc=$?"
ls -l dernier
```

```text
rc=0
lrwxrwxrwx. 1 ansible ansible 19 Jul 22 14:00 dernier -> stock/archives-2025
```

**`ln -sfn`** est donc le réflexe pour repointer un lien vers un répertoire.
L'alternative, tout aussi sûre, est de supprimer le lien puis de le recréer.

### Supprimer un lien : la barre oblique finale est un piège

Sur un lien symbolique vers un répertoire, `rm` a quatre comportements selon
qu'on écrit `-r` ou non, et qu'on met une barre oblique finale ou non. Les
quatre essais qui suivent repartent à chaque fois de la **même** structure :

```text
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
./lien          (lien -> cible)
```

**`rm lien`** : le cas normal, et le bon.

```bash
rm lien ; echo "rc=$?" ; find .
```

```text
rc=0
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
```

Seul le lien disparaît, la cible et tout son contenu sont intacts.

**`rm -r lien`** : rigoureusement identique. Sans barre oblique, `rm` ne
traverse pas le lien, même avec `-r`.

```text
rc=0
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
```

**`rm lien/`** : refus net, rien n'est touché.

```bash
rm lien/ ; echo "rc=$?" ; find .
```

```text
rm: cannot remove 'lien/': Is a directory
rc=1
.
./cible
./cible/sous
./cible/sous/b.txt
./cible/a.txt
./lien
```

**`rm -r lien/`** : le piège.

```bash
rm -r lien/ ; echo "rc=$?" ; find .
```

```text
rm: cannot remove 'lien/': Not a directory
rc=1
.
./cible
./lien
```

Lisez cette dernière sortie deux fois. `rm` a signalé une **erreur** et rendu un
code de retour **1**, mais il avait d'abord vidé récursivement `cible/` :
`a.txt`, `sous/` et `b.txt` ont disparu. Le lien, lui, est toujours là, et le
répertoire visé existe encore, vide. La commande a donc échoué à faire ce qu'on
lui demandait, et réussi à détruire ce qu'on ne voulait pas perdre.

L'explication tient à la règle vue plus haut : la barre oblique finale force la
traversée du lien. Le `-r` s'applique donc au **répertoire au bout**, dont il
efface le contenu ; puis `rm` essaie de supprimer l'entrée `lien/`, qui n'est
pas un répertoire, et échoue.

> Ne mettez jamais de barre oblique finale sur un lien symbolique que vous
> voulez supprimer. Le guide rappelle que `rm` est irréversible : ici, un seul
> caractère en trop en fait la démonstration.

Une commande évite tout doute, parce qu'elle ne sait faire qu'une chose,
supprimer une entrée de répertoire, et refuse les répertoires :

```bash
unlink lien ; echo "rc=$?"
unlink cible ; echo "rc=$?"
```

```text
rc=0
unlink: cannot unlink 'cible': Is a directory
rc=1
```

### Retrouver tous les noms d'un fichier

Un lien symbolique se voit dans `ls -l`. Un lien physique, non : rien ne
distingue les deux noms. Seul le compteur trahit qu'il en existe un autre, sans
dire où. Trois commandes répondent à la question.

```bash
cd ~/atelier-liens
ln rapport.log stock/archives/backup-rapport.log
ls -li rapport.log stock/archives/backup-rapport.log
```

```text
309333 -rw-------. 2 ansible ansible 66 Jul 22 13:58 rapport.log
309333 -rw-------. 2 ansible ansible 66 Jul 22 13:58 stock/archives/backup-rapport.log
```

```bash
find ~/atelier-liens -samefile rapport.log         # par comparaison de fichier
find ~/atelier-liens -xdev -inum 309333            # par numero d inode
find ~/atelier-liens -type f -links +1 -printf "%n %p\n"   # tous les fichiers multi-noms
```

```text
/home/ansible/atelier-liens/rapport.log
/home/ansible/atelier-liens/stock/archives/backup-rapport.log
/home/ansible/atelier-liens/rapport.log
/home/ansible/atelier-liens/stock/archives/backup-rapport.log
2 /home/ansible/atelier-liens/rapport.log
2 /home/ansible/atelier-liens/stock/archives/backup-rapport.log
```

`-samefile` est le plus sûr : il n'exige pas de connaître le numéro. `-inum`
suppose que vous restiez sur le même système de fichiers, d'où le `-xdev`.

Le compteur a une conséquence pratique sur le calcul d'espace : `du` ne compte
un inode **qu'une fois**, même s'il le rencontre sous plusieurs noms.

```bash
du -ch  --apparent-size rapport.log stock/archives/backup-rapport.log
du -clh --apparent-size rapport.log stock/archives/backup-rapport.log
```

```text
66	rapport.log
66	total
```

```text
66	rapport.log
66	stock/archives/backup-rapport.log
132	total
```

Sans `-l`, `du` n'affiche même pas le second nom, et le total reste à 66 : c'est
la place réellement occupée. Avec `-l`, il compte chaque nom et annonce 132, ce
qui est faux en termes d'occupation disque. C'est ainsi que des sauvegardes par
liens physiques peuvent contenir dix « copies » d'une arborescence sans occuper
dix fois la place.

### Copier : ce qui suit le lien et ce qui le préserve

Une fois les liens en place, la façon de les copier décide de ce qu'on obtient à
l'arrivée.

```bash
mkdir -p /tmp/essai-copie && cd /tmp/essai-copie
echo contenu > source.txt
ln -s source.txt lien.txt
cp    lien.txt clone-defaut.txt     # suit le lien : copie du CONTENU
cp -P lien.txt clone-P.txt          # preserve le lien
cp -a lien.txt clone-a.txt          # archive : preserve aussi
cp -l source.txt clone-dur.txt      # cree un LIEN PHYSIQUE, pas une copie
ls -li
```

```text
total 12
17458672 lrwxrwxrwx. 1 ansible ansible 10 Jul 22 14:01 clone-a.txt -> source.txt
17458670 -rw-r--r--. 1 ansible ansible  8 Jul 22 14:01 clone-defaut.txt
17458668 -rw-r--r--. 2 ansible ansible  8 Jul 22 14:01 clone-dur.txt
17458671 lrwxrwxrwx. 1 ansible ansible 10 Jul 22 14:01 clone-P.txt -> source.txt
17458669 lrwxrwxrwx. 1 ansible ansible 10 Jul 22 14:01 lien.txt -> source.txt
17458668 -rw-r--r--. 2 ansible ansible  8 Jul 22 14:01 source.txt
```

Quatre résultats différents pour quatre commandes :

- `clone-defaut.txt` est un **fichier ordinaire**, inode neuf : `cp` a suivi le
  lien et copié le contenu ;
- `clone-P.txt` et `clone-a.txt` sont des **liens symboliques**, inodes propres,
  même cible ;
- `clone-dur.txt` partage l'inode `17458668` de `source.txt`, dont le compteur
  est passé à `2` : `cp -l` n'a rien copié du tout.

Retenez `cp -a` pour recopier une arborescence sans dénaturer ses liens, et
`cp -l` quand vous voulez explicitement un second nom.

### Des liens partout dans le système

Ces deux mécanismes ne sont pas des curiosités d'exercice : le système en est
rempli.

```bash
ls -l /etc/localtime
readlink -f /etc/localtime
ls -l /usr/bin/python3
```

```text
lrwxrwxrwx. 1 root root 25 May 26 15:21 /etc/localtime -> ../usr/share/zoneinfo/UTC
/usr/share/zoneinfo/UTC
lrwxrwxrwx. 1 root root 10 Apr 16 00:00 /usr/bin/python3 -> python3.12
```

Le fuseau horaire est un lien symbolique **relatif** vers un fichier de la base
`zoneinfo` : changer de fuseau, c'est repointer ce lien. `/usr/bin/python3` est
un lien vers la version réellement installée, ce qui permet aux scripts de ne
jamais nommer un numéro de version.

`namei -l` déroule tout un chemin, lien par lien :

```bash
namei -l /etc/localtime
```

```text
f: /etc/localtime
dr-xr-xr-x root root /
drwxr-xr-x root root etc
lrwxrwxrwx root root localtime -> ../usr/share/zoneinfo/UTC
dr-xr-xr-x root root   ..
drwxr-xr-x root root   usr
drwxr-xr-x root root   share
drwxr-xr-x root root   zoneinfo
-rw-r--r-- root root   UTC
```

Les liens physiques sont plus discrets, mais présents eux aussi, souvent pour
qu'un même binaire réponde à plusieurs noms :

```bash
find /usr/bin -maxdepth 1 -type f -links +1 -printf "%n %i %p\n" | sort -k2
```

```text
2 17458311 /usr/bin/named-checkzone
2 17458311 /usr/bin/named-compilezone
```

Deux commandes, un seul programme sur le disque. Et il adapte bel et bien son
comportement au nom sous lequel il est appelé :

```bash
named-checkzone   2>&1 | head -1 | cut -c1-40
named-compilezone 2>&1 | head -2 | tail -1 | cut -c1-40
```

```text
usage: named-checkzone [-djqvD] [-c clas
usage: named-compilezone [-djqvD] [-c cl
```

L'un accepte de tourner sans `-o`, l'autre répond d'abord
`output file required, but not specified`. Même inode, deux interfaces.

### Dépannage

| Symptôme | Cause probable |
|---|---|
| `hard link not allowed for directory` | `ln` sans `-s` sur un répertoire ; seul le lien symbolique le permet |
| `Invalid cross-device link` | la source et la destination ne sont pas sur le même système de fichiers ; le vérifier avec `df` ou `stat -c %D` |
| `failed to access '…': No such file or directory` au `ln` | un lien physique exige une cible existante ; `ln -s` l'accepte absente |
| `Operation not permitted` au `ln` alors que le répertoire est accessible | `fs.protected_hardlinks = 1` : on ne lie pas un fichier qu'on ne possède pas |
| `cat: …: No such file or directory` sur un fichier bien listé par `ls` | lien pendant ; le confirmer avec `test -L`, le retrouver avec `find -xtype l` |
| Le lien a cessé de fonctionner après un déplacement | lien relatif déplacé sans sa cible ; le refaire, ou le passer en absolu |
| `ln -sf` sur un lien vers un répertoire ne change rien | le lien a été traversé, le nouveau lien a été créé dedans ; utiliser `ln -sfn` |
| `rm: cannot remove 'lien/': Not a directory` | barre oblique finale sur un lien ; **le contenu de la cible vient d'être effacé** |
| `rm: cannot remove 'lien/': Is a directory` | barre oblique finale sans `-r` ; rien n'a été supprimé, retirer la barre |
| Le compteur de liens d'un répertoire ne vaut pas 1 | normal : 2 plus un par sous-répertoire, à cause des `.` et `..` |
| `du` annonce moins que la somme des fichiers | des liens physiques partagent le même inode, compté une seule fois |
| La copie a perdu les liens symboliques | `cp` les suit par défaut ; utiliser `cp -a` (ou `cp -P`) |

### Défaire la démonstration

```bash
cd ~
rm -rf ~/atelier-liens /tmp/essai /tmp/essai-copie
sudo umount /mnt/annexe
sudo rmdir /mnt/annexe
sudo wipefs -a /dev/vdb
```

Vérifiez qu'il ne reste rien : `lsblk` ne doit plus afficher de point de montage
pour `vdb`, et `find ~ -xtype l` ne doit rien renvoyer.

# Drill — partitions, LVM et swap

**5 tâches, 100 points, 25 minutes. Aucun indice.** Partagé entre RHCSA et LFCS :
`parted`, LVM, XFS et le swap se comportent à l'identique sur AlmaLinux et sur
Ubuntu. Le disque supplémentaire `/dev/vdb` est attaché et vierge.

## Ce qu'est un drill

Un drill n'est pas un lab. Il n'y a pas de cours ici, et c'est délibéré : vous
êtes en conditions d'examen. On vous donne un énoncé, un chronomètre et une
machine, et vous devez retrouver seul des gestes que vous avez déjà pratiqués.

La différence avec un lab tient en trois points :

- **aucun indice n'est disponible**, même contre des points ;
- **le temps compte** : 25 minutes pour cinq tâches, c'est le rythme de
  l'examen, pas celui de l'apprentissage ;
- **les tâches se suivent**. C'est la particularité du stockage : la chaîne va de
  la partition au montage, et un maillon manquant rend sans valeur tout ce qui
  vient après. Si un maillon résiste, réparez-le avant d'avancer.

Le seuil de réussite est fixé à **70 points sur 100**.

## Ce qu'il faut savoir avant de le tenter

C'est le sujet où les candidats perdent le plus de points, parce que la chaîne
est longue et qu'aucun raccourci n'existe. Si l'un des maillons ci-dessous ne
vous est pas familier, jouez le lab correspondant **avant** : vous y trouverez le
cours, les indices et le droit à l'erreur que le drill ne vous donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Table de partitions GPT et découpage d'un disque | `l2-partition-gpt` |
| Volume physique, groupe de volumes, volume logique | `l2-lvm-extend-persist` |
| Étendre un volume et faire suivre le système de fichiers | `l2-lvm-extend-persist` |
| Créer et étiqueter un système de fichiers XFS | `l2-filesystem-create-xfs` |
| Monter par UUID de façon persistante | `l2-fstab-persist-uuid` |
| Créer, activer et rendre le swap persistant | `l2-swap-management` |
| Lire l'espace réellement disponible, et ce qui le mange | `l2-disk-space-troubleshoot` |

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt-cinq minutes
passent vite, et le premier réflexe d'examen consiste à **lire les cinq tâches
d'abord** pour voir comment elles s'enchaînent.

Trois précautions propres au stockage, et la première prime sur tout :

- **ne vous trompez jamais de disque**. Lancez `lsblk -f` avant chaque commande
  destructrice et lisez la sortie en entier : le disque cible doit être celui que
  l'énoncé désigne, et il ne doit rien porter de monté. Une table de partitions
  écrasée sur le mauvais disque ne se rattrape pas en vingt-cinq minutes ;
- **vérifiez maillon par maillon**, avec l'outil de chaque étage plutôt qu'avec
  votre mémoire : `lsblk` pour les partitions, `pvs`, `vgs` et `lvs` pour LVM,
  `blkid` pour l'UUID et le type de système de fichiers, `findmnt` pour ce qui est
  réellement monté, `swapon --show` pour le swap. Chacun de ces cinq outils dit
  une chose que les autres ne disent pas ;
- **testez `/etc/fstab` avant de partir**. Une entrée fautive n'a aucun effet
  visible tout de suite et bloque le démarrage plus tard. Après avoir écrit vos
  lignes, démontez et relancez `mount -a` : si la commande passe en silence, la
  persistance tient.

Un piège classique et coûteux : agrandir un volume logique n'agrandit pas le
système de fichiers qu'il porte. Tant que `df -h` n'affiche pas la nouvelle
taille, l'espace n'existe pas pour les utilisateurs, et la tâche vaut zéro.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

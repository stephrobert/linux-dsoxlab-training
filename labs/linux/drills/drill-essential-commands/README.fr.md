# Drill — commandes essentielles

**5 tâches, 100 points, 20 minutes. Aucun indice.** Partagé entre RHCSA et LFCS :
ces commandes se comportent à l'identique sur AlmaLinux et sur Ubuntu, vous
choisissez la cible qui vous arrange.

## Ce qu'est un drill

Un drill n'est pas un lab. Il n'y a pas de cours ici, et c'est délibéré : vous
êtes en conditions d'examen. On vous donne un énoncé, un chronomètre et une
machine, et vous devez retrouver seul des gestes que vous avez déjà pratiqués.

La différence avec un lab tient en trois points :

- **aucun indice n'est disponible**, même contre des points ;
- **le temps compte** : 20 minutes pour cinq tâches, c'est le rythme de
  l'examen, pas celui de l'apprentissage ;
- **les tâches sont indépendantes**. Si l'une résiste, passez à la suivante et
  revenez-y : une tâche non traitée coûte moins cher qu'un chronomètre épuisé
  sur la première.

Le seuil de réussite est fixé à **70 points sur 100**.

## Ce qu'il faut savoir avant de le tenter

Ce drill révise la boîte à outils de base, celle que les deux certifications
supposent acquise. Si l'un de ces sujets ne vous est pas familier, jouez le lab
correspondant **avant** : vous y trouverez le cours, les indices et le droit à
l'erreur que le drill ne vous donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Chercher des fichiers sur autre chose que leur nom | `l1-find-files` |
| Créer une archive compressée et vérifier son contenu | `l1-tar-archives` |
| Filtrer des lignes avec `grep` et les expressions régulières | `l1-grep-regex` |
| Découper, trier, compter : `cut`, `sort`, `uniq`, `awk` | `l1-text-processing` |
| Liens physiques et liens symboliques, et ce qui les distingue | `l1-links-hard-sym` |
| Propriétaire, groupe et droits en notation octale | `l1-permissions-ugo` |
| Séparer la sortie standard de la sortie d'erreur | `l1-redirections-pipes` |

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt minutes passent
vite, et le premier réflexe d'examen consiste à **lire les cinq tâches d'abord**
pour repérer celles qui se traitent en une commande.

Trois habitudes qui font gagner des points sur ce drill en particulier :

- **construisez vos commandes par étapes**. Une chaîne de traitement écrite d'un
  seul jet est presque toujours fausse. Affichez d'abord la liste de fichiers ou
  les lignes retenues, comptez-les, puis seulement branchez la suite ;
- **contrôlez le livrable, pas la commande**. On ne note pas ce que vous avez
  tapé mais ce que la machine contient : listez le contenu d'une archive avec
  `tar -tzf`, comparez deux inodes avec `ls -li`, relisez propriétaire et mode
  avec `stat`, et ouvrez un fichier de sortie avec `cat -A` si un espace de fin
  vous inquiète ;
- **méfiez-vous du bruit**. Quand un fichier doit contenir une seule information,
  un en-tête, une ligne vide ou un message d'erreur mêlé au flux le rend faux.
  Regardez toujours ce qui est réellement écrit avant de passer à la suite.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

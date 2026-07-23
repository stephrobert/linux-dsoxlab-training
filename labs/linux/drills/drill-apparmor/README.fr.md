# Drill — AppArmor

**4 tâches, 100 points, 15 minutes. Aucun indice.** Ce drill est **LFCS
uniquement** : il ne se joue que sur Ubuntu 24.04, il n'y a pas de cible
AlmaLinux. Côté RHEL, le contrôle d'accès obligatoire s'appelle SELinux et fait
l'objet de `drill-selinux`.

## Ce qu'est un drill

Un drill n'est pas un lab. Il n'y a pas de cours ici, et c'est délibéré : vous
êtes en conditions d'examen. On vous donne un énoncé, un chronomètre et une
machine, et vous devez retrouver seul des gestes que vous avez déjà pratiqués.

La différence avec un lab tient en trois points :

- **aucun indice n'est disponible**, même contre des points ;
- **le temps compte** : c'est le drill le plus court du dépôt, 15 minutes pour
  quatre tâches. Une lecture d'énoncé qui traîne mange déjà un cinquième du
  budget ;
- **les tâches sont indépendantes**. Si l'une résiste, passez à la suivante et
  revenez-y : une tâche non traitée coûte moins cher qu'un chronomètre épuisé
  sur la première.

Le seuil de réussite est fixé à **70 points sur 100**.

## Ce qu'il faut savoir avant de le tenter

AppArmor est le sujet le moins bien couvert par les labs du dépôt : soyez
prévenu avant de lancer le chronomètre.

| Ce que le drill exerce | Où c'est traité |
|---|---|
| Le raisonnement d'un contrôle d'accès obligatoire : mode d'application contre mode observation, et lire un refus dans le journal | `l4-selinux-diagnose-avc` (côté RHEL : l'outil diffère, la logique non) |
| Piloter les profils AppArmor eux-mêmes et lire leur mode | `lfcs-apparmor` (lab jouable, mais son README renvoie au guide : il n'y a pas de cours sur place) |

Autrement dit, la révision se fait dans le guide en ligne, pas dans un lab. Si
vous n'avez jamais lu la sortie de `aa-status`, faites-le une fois **avant** de
démarrer le chrono : quinze minutes ne laissent pas le temps de découvrir un
format d'affichage.

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après, et **lisez les quatre
tâches d'abord** : elles portent toutes sur le même mécanisme, et les traiter
dans le désordre ne coûte rien.

Trois habitudes propres à AppArmor :

- **la source de vérité est `aa-status`, pas le contenu de `/etc/apparmor.d/`**.
  Un profil peut exister sur le disque sans être chargé, être chargé dans un mode
  différent de celui qu'indique son fichier, ou avoir été rechargé depuis. Ne
  concluez jamais depuis un fichier : lisez l'état chargé ;
- **relevez le nom exact d'un profil avant de le manipuler**. Les profils ne sont
  pas nommés uniformément : certains portent un nom court, d'autres le chemin
  complet du binaire. Une commande adressée à un nom qui n'existe pas échoue en
  silence ou touche un autre profil que celui visé. Repartez de la sortie de
  `aa-status` plutôt que de saisir un nom de mémoire ;
- **« chargé » n'est pas « appliqué »**. Le mode observation journalise sans
  bloquer, le mode application bloque. Ce sont deux comptages séparés dans la
  sortie de l'outil : après chaque changement, relisez celle-ci et vérifiez que
  votre profil a bien changé de colonne.

Dernier point qui trompe : la machine livre par défaut certains profils en mode
observation, sans que vous y soyez pour rien. Notez l'état de départ avant de
toucher à quoi que ce soit, vous saurez ainsi ce que vous avez réellement changé.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

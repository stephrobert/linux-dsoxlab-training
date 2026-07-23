# Drill — utilisateurs, groupes et délégation

**5 tâches, 100 points, 20 minutes. Aucun indice.** Partagé entre RHCSA et LFCS.

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

Ce drill révise cinq sujets. Si l'un d'eux ne vous est pas familier, jouez le
lab correspondant **avant** : vous y trouverez le cours, les indices et le droit
à l'erreur que le drill ne vous donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Créer un compte avec des attributs imposés, le supprimer proprement | `l2-user-lifecycle` |
| Vieillissement du mot de passe et expiration de compte | `l2-password-policy` |
| Répertoire partagé, bit set-GID, droits collectifs | `l2-collaborative-setgid` |
| Déléguer sudo au plus juste, sans donner tous les droits | `l2-sudo-delegation` |
| Lire et poser des droits Unix | `l1-permissions-ugo` |

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt minutes passent
vite, et le premier réflexe d'examen consiste à **lire les cinq tâches d'abord**
pour repérer celles qui se traitent en une commande.

Deux habitudes qui font gagner des points, sur ce drill comme en examen :

- **vérifiez chaque tâche juste après l'avoir faite**, avec la commande qui lit
  l'état du système et non votre mémoire (`id`, `getent`, `chage -l`,
  `ls -ld`, `sudo -l -U`). Une tâche que l'on croit finie et qui ne l'est pas
  coûte le même prix qu'une tâche non commencée ;
- **ne vous verrouillez pas dehors**. Ce drill touche aux comptes et à `sudo` :
  gardez une seconde session ouverte avant de modifier quoi que ce soit à
  l'authentification, et validez toute modification de `sudoers` par
  `visudo -c` avant de fermer cette session.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

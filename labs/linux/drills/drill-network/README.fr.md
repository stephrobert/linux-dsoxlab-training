# Drill — réseau statique

**4 tâches, 100 points, 20 minutes. Aucun indice.** Partagé entre RHCSA et LFCS :
le sujet ne nomme aucun outil, vous employez celui de votre distribution
(`nmcli` sur AlmaLinux, `netplan` sur Ubuntu). Tout se joue sur l'interface
dédiée `lab0`, **jamais** sur l'interface de gestion, et tout est vérifié
**après un rechargement du réseau**.

## Ce qu'est un drill

Un drill n'est pas un lab. Il n'y a pas de cours ici, et c'est délibéré : vous
êtes en conditions d'examen. On vous donne un énoncé, un chronomètre et une
machine, et vous devez retrouver seul des gestes que vous avez déjà pratiqués.

La différence avec un lab tient en trois points :

- **aucun indice n'est disponible**, même contre des points ;
- **le temps compte** : 20 minutes pour quatre tâches, c'est le rythme de
  l'examen, pas celui de l'apprentissage ;
- **les tâches sont indépendantes**. Si l'une résiste, passez à la suivante et
  revenez-y : une tâche non traitée coûte moins cher qu'un chronomètre épuisé
  sur la première.

Le seuil de réussite est fixé à **70 points sur 100**.

## Ce qu'il faut savoir avant de le tenter

Ce drill sépare deux choses que l'on confond souvent : configurer une interface,
et rendre cette configuration vivante après rechargement. Si l'un des sujets
ci-dessous ne vous est pas familier, jouez le lab correspondant **avant** : vous
y trouverez le cours, les indices et le droit à l'erreur que le drill ne vous
donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Poser une adresse statique dans un profil qui survit au rechargement | `l4-network-static-persist` |
| Comprendre pourquoi une commande tapée à la main ne persiste pas | `l4-network-static-persist` |
| Lire l'état réel d'un lien et d'une route | `l4-network-troubleshoot` |
| Résoudre un nom sans serveur DNS, et le prouver avec `getent hosts` | `l4-network-troubleshoot` |

Côté Ubuntu, `netplan` fait l'objet du lab `lfcs-netplan-static`. Attention : son
README ne contient pas encore de cours sur place, il renvoie au guide en ligne.

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt minutes passent
vite, et le premier réflexe d'examen consiste à **lire les quatre tâches
d'abord** pour repérer celles qui se traitent en une commande.

Trois précautions propres au réseau :

- **identifiez d'abord l'interface à ne pas toucher**. Son nom change selon la
  distribution et l'hyperviseur, donc ne le devinez pas : demandez-le au système
  avec `ip route get 1.1.1.1`, qui vous donne l'interface qui porte votre session.
  Tout ce que vous faites ensuite se passe ailleurs. Une interface de gestion
  coupée, c'est la machine perdue et le drill avec ;
- **configuré n'est pas actif**. Écrire une adresse dans un profil ou dans un
  fichier YAML ne la met pas en place, et l'appliquer à la main ne l'écrit nulle
  part. Le contrôle recharge le réseau avant de regarder : prenez l'habitude de
  recharger vous-même, puis de relire l'état avec `ip addr show` et `ip route`,
  jamais en relisant votre propre fichier ;
- **la résolution de noms ne se teste pas avec `dig`**. `dig` interroge un
  serveur et ignore la résolution locale : c'est `getent hosts` qui suit le même
  chemin que les applications, et donc le seul verdict qui vaille ici.

Un détail qui coûte des points sur Ubuntu : un fichier de configuration réseau
trop permissif est refusé ou signalé. Vérifiez ses droits avant de conclure que
votre syntaxe est en cause.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

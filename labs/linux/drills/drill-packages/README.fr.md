# Drill — gestion des paquets

**5 tâches, 100 points, 20 minutes. Aucun indice.** Partagé entre RHCSA et LFCS :
le sujet ne nomme aucun outil, vous employez celui de votre distribution (`dnf`
sur AlmaLinux, `apt` sur Ubuntu). L'objectif est le même des deux côtés, seule la
commande change.

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

Installer et supprimer n'est que la moitié du sujet : l'autre moitié consiste à
**interroger** la base de paquets, ce qui est justement ce qu'on ne pratique
jamais spontanément. Si l'un des sujets ci-dessous ne vous est pas familier,
jouez le lab correspondant **avant** : vous y trouverez le cours, les indices et
le droit à l'erreur que le drill ne vous donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Installer, supprimer, et prouver l'état d'un paquet | `l2-package-management` |
| Retrouver quel paquet fournit un fichier donné | `l2-package-management` |
| Lister ce qu'un paquet a posé sur le disque | `l2-package-management` |
| D'où viennent les paquets : dépôts, priorités, signature | `l2-repo-configure` |

Côté Ubuntu, `apt` et `dpkg` font l'objet du lab `lfcs-package-apt`. Attention :
son README ne contient pas encore de cours sur place, il renvoie au guide en
ligne. Le gel d'un paquet contre les mises à jour n'a, lui, de lab dédié dans
aucune des deux familles : c'est le point à réviser dans le guide avant de vous
lancer.

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt minutes passent
vite, et le premier réflexe d'examen consiste à **lire les cinq tâches d'abord**
pour repérer celles qui se traitent en une commande.

Trois habitudes propres à ce sujet :

- **interrogez, ne devinez pas**. Le paquet qui fournit une commande ne porte pas
  forcément le nom de cette commande, et ce nom diffère d'une distribution à
  l'autre. C'est précisément pour cela que les deux familles offrent une commande
  d'interrogation par fichier : servez-vous-en plutôt que de reconstituer un nom
  de mémoire ;
- **quand un fichier de sortie est demandé, écrivez exactement ce qui est
  demandé**. Une sortie brute contient souvent une version, une architecture, un
  en-tête ou une ligne de résumé. Relisez le fichier produit avant de passer à la
  suite : une ligne de trop vaut zéro comme une réponse fausse ;
- **prouvez l'état, pas l'action**. Une commande d'installation qui rend la main
  sans erreur ne prouve rien, notamment si le paquet était déjà là ou si la
  transaction a été annulée. Rejouez toujours la commande d'interrogation après
  coup, et pour un paquet gelé, vérifiez qu'il figure bien dans la liste des
  paquets gelés plutôt que de faire confiance au message affiché.

Un réflexe qui fait gagner du temps : quand la syntaxe vous échappe, `man` et
`--help` sont autorisés le jour de l'examen. Les consulter coûte trente secondes,
une commande fausse en coûte cinq minutes.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

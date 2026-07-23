# Drill — pare-feu

**5 tâches, 100 points, 20 minutes. Aucun indice.** Partagé entre RHCSA et LFCS :
le sujet ne nomme aucun outil, vous employez celui de votre distribution
(`firewalld` sur AlmaLinux, `ufw` sur Ubuntu). Vos règles sont vérifiées
**après un rechargement du pare-feu**.

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

Ce drill ne mesure pas votre connaissance d'un outil, mais votre maîtrise d'une
distinction : ce qui est actif maintenant contre ce qui est écrit sur le disque.
Si ce partage ne vous est pas familier, jouez le lab correspondant **avant** :
vous y trouverez le cours, les indices et le droit à l'erreur que le drill ne
vous donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Zones, règle temporaire contre règle permanente, rechargement | `l4-firewall-persist` |
| Ouvrir un service nommé ou un port numéroté, et lire l'écart entre les deux listes | `l4-firewall-persist` |
| Savoir si un port écoute vraiment, et qui le filtre | `l4-network-troubleshoot` |

Côté Ubuntu, `ufw` fait l'objet du lab `lfcs-firewall-ufw`. Attention : son
README ne contient pas encore de cours sur place, il renvoie au guide en ligne.
Le raisonnement, lui, est celui de `l4-firewall-persist`.

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt minutes passent
vite, et le premier réflexe d'examen consiste à **lire les cinq tâches d'abord**
pour repérer celles qui se traitent en une commande.

Trois précautions propres au pare-feu, dans l'ordre où elles comptent :

- **ne coupez pas votre propre session**. Vous travaillez à travers SSH : perdre
  l'accès, c'est perdre le drill. Ouvrez une **seconde session** avant d'activer
  quoi que ce soit, et assurez-vous que SSH est autorisé **avant** de mettre le
  pare-feu en marche, jamais après ;
- **rechargez, puis vérifiez**. Une règle qui ne survit pas au rechargement ne
  vaut rien, et c'est exactement ce que le contrôle mesure. Prenez l'habitude de
  recharger vous-même, puis de relire l'état complet du pare-feu (`firewall-cmd
  --list-all` ou `ufw status verbose`) : la liste affichée après rechargement est
  la seule qui compte ;
- **ne confondez pas les trois comportements possibles**. Un port peut être
  autorisé, simplement non autorisé, ou refusé de façon explicite. Ces trois cas
  ne se lisent pas au même endroit dans la sortie de l'outil : lisez la ligne, ne
  déduisez pas.

Un dernier réflexe : quand un port n'est pas dans la zone que vous croyez, ce
n'est pas la règle qui est fausse, c'est la zone. Vérifiez à quelle zone votre
interface est rattachée avant de soupçonner la syntaxe.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.

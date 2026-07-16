# Contexte — le cycle de vie d'un compte, contre la montre

Créer un utilisateur est trivial. Créer **le bon** utilisateur, avec le bon UID,
les bons groupes, une politique de vieillissement qui s'applique vraiment, une
délégation qui accorde exactement le nécessaire et rien de plus, et fermer un
compte de façon qu'il soit réellement fermé — voilà le métier.

Ce drill est un **chrono** : 5 tâches, 20 minutes, aucun indice. Les mêmes
compétences servent RHCSA et LFCS — `useradd`, `usermod`, `chage` et `sudoers`
se comportent à l'identique sur RHEL et Debian.

Deux pièges que tu retrouveras à l'examen :

- un **compte** qui expire n'est **pas** la même chose qu'un **mot de passe** qui
  expire ;
- verrouiller un mot de passe ne **ferme pas** un compte : le shell doit aussi
  interdire la connexion, sinon une clé SSH passe encore.

Lis le sujet : `dsoxlab challenge drill-users-groups`.

# Contexte — AppArmor, l'autre MAC

Debian et Ubuntu n'utilisent pas SELinux : ils utilisent **AppArmor**. Même but
— confiner un programme à ce dont il a légitimement besoin — mais un modèle
différent. AppArmor lie un profil à un **chemin**, là où SELinux étiquette
chaque objet.

Deux modes, et toute la différence est là :

- **complain** : le profil journalise les violations mais ne bloque rien. C'est
  là qu'on construit un profil, ou qu'on diagnostique ;
- **enforce** : le profil bloque réellement. C'est là qu'on le laisse.

Un profil oublié en complain ne protège rien — il prend des notes. C'est
l'erreur que ce drill traque.

**Chrono** : 4 tâches, 15 minutes, aucun indice. LFCS uniquement — RHEL a
SELinux, travaillé dans `drill-selinux`.

Lis le sujet : `dsoxlab challenge drill-apparmor`.

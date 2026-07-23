# Contexte — AppArmor, l'autre MAC

Debian et Ubuntu n'utilisent pas SELinux : ils utilisent **AppArmor**. Même but,
confiner un programme à ce dont il a légitimement besoin, mais un modèle
différent. AppArmor lie un profil à un **chemin**, là où SELinux étiquette
chaque objet.

Un profil peut être chargé et ne rien protéger du tout : il existe un mode où il
se contente de prendre des notes. C'est cette illusion de protection que ce
drill traque.

**Chrono** : 4 tâches, 15 minutes, aucun indice. LFCS uniquement ; RHEL a
SELinux, travaillé dans `drill-selinux`.

Lis le sujet : `dsoxlab challenge drill-apparmor`.

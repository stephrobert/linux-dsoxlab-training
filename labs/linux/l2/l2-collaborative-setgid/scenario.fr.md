# Contexte — un répertoire partagé qui partage vraiment

Le groupe `devteam` (alice, bob) a besoin d'un répertoire commun, `/srv/partage`,
où chacun dépose des fichiers que **tout le groupe** peut ensuite modifier. Pour
l'instant il appartient à `root:root` et chaque fichier créé garde le groupe *de
son auteur* — donc la collaboration casse. La solution : le **bit set-GID** sur le
répertoire.

Ta mission, sur la VM :

1. Donne à `/srv/partage` le groupe **`devteam`** (`chgrp devteam /srv/partage`).
2. Pose le mode **`2775`** — le `2` de tête est le bit set-GID, plus `rwxrwxr-x`
   (`chmod 2775 /srv/partage`).

L'idée : sur un **répertoire**, le bit set-GID fait que tout nouveau fichier
dedans hérite du groupe du répertoire au lieu du groupe primaire de son créateur —
la condition pour qu'un dossier partagé soit vraiment collaboratif. `ls -ld`
montre un `s` à la place de l'exécution du groupe.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/

# Contexte — SELinux, et ce qui ne survit pas

Le réflexe qui fait échouer les candidats RHCSA : `setenforce 1` et on passe à
la suite. Ça marche — jusqu'au reboot. Pareil avec `chcon` : le contexte est
bon, le service démarre, et la première relabellisation l'efface.

SELinux a un **runtime** et une **policy**. Ce que tu changes au runtime est
temporaire. Ce que tu écris dans la policy survit. Chaque tâche de ce drill est
bâtie sur cette distinction.

Ce drill est un **chrono** : 4 tâches, 20 minutes, aucun indice. RHCSA
uniquement — Debian a AppArmor, un modèle entièrement différent, travaillé dans
`drill-apparmor`.

Tes contextes sont vérifiés **après une relabellisation**. Choisis ton outil en
conséquence.

Lis le sujet : `dsoxlab challenge drill-selinux`.

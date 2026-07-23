# Contexte — SELinux, et ce qui ne survit pas

Le réflexe qui fait échouer les candidats RHCSA : basculer SELinux en enforcing
à la volée, et passer à la suite. Ça marche, jusqu'au reboot. Même histoire avec
un contexte de fichier posé à la main : le service démarre, tout va bien, et la
première relabellisation l'efface.

SELinux a un **runtime** et une **policy**. Ce que tu changes au runtime est
temporaire, ce que tu écris dans la policy survit. Chaque tâche de ce drill est
bâtie sur cette distinction.

Ce drill est un **chrono** : 4 tâches, 20 minutes, aucun indice. RHCSA
uniquement ; Debian a AppArmor, un modèle entièrement différent, travaillé dans
`drill-apparmor`.

Lis le sujet : `dsoxlab challenge drill-selinux`.

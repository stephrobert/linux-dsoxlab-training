# Contexte — le LFCS, en conditions d'examen

Ce capstone n'est pas un lab : c'est un **examen blanc**. Aucun indice, aucun
pas-à-pas, un chrono et un score de réussite. Il couvre les **5 domaines
officiels du LFCS** dans leurs poids réels :

| Domaine | Poids | Tâches |
|---|---|---|
| Essential Commands | 20 % | 1–4 |
| Operations Deployment | 25 % | 5–8 |
| Users and Groups | 10 % | 9–10 |
| Networking | 25 % | 11–14 |
| Storage | 20 % | 15–17 |

**17 tâches, 100 points, 120 minutes, 70/100 pour réussir.**

Tout se passe sur une seule VM Ubuntu 24.04 — le LFCS est multi-distrib, et
cette session en est le versant Debian.

La règle qui fait échouer les candidats : la **persistance**. Une règle de
pare-feu qui disparaît au reboot, un montage absent de `/etc/fstab`, un service
démarré mais pas `enabled` — tout ça vaut zéro. Les tests lisent l'état du
système, pas les commandes que tu as tapées.

Lis le sujet : `dsoxlab challenge lfcs-mock-exam`.

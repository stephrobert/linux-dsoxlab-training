# Contexte — exécuter quelque chose une fois, plus tard

Cron répète une tâche selon un planning. Mais parfois tu veux qu'une commande
s'exécute **une seule fois**, à une heure précise, et plus jamais — une
maintenance ce soir, un rappel dans une heure. C'est le rôle d'**`at`**.

Ta mission, sur la VM :

1. Planifie la commande **`touch /run/rapport.done`** pour s'exécuter **une fois,
   dans le futur** (par exemple `at now + 1 hour`, ou une heure précise comme
   `at 23:00`). Passe la commande par un pipe :
   `echo 'touch /run/rapport.done' | at now + 1 hour`.
2. Confirme qu'elle est en file avec **`atq`**, et inspecte son contenu avec
   **`at -c <numéro>`**.

L'idée : `at` lit la commande sur l'entrée standard et met en file une tâche
**ponctuelle** gérée par `atd` ; `atq` liste les tâches en attente, `at -c`
affiche le script d'une tâche, et `atrm` en supprime une. Contrairement à cron,
elle ne se répète pas.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/

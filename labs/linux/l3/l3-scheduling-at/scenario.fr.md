# Contexte — exécuter quelque chose une fois, plus tard

Cron répète une tâche selon un planning. Mais parfois tu veux qu'une commande
s'exécute **une seule fois**, à une heure précise, et plus jamais — une
maintenance ce soir, un rappel dans une heure. C'est le rôle d'**`at`**.

L'idée : une tâche ponctuelle est mise en file d'attente, puis confiée à un démon
qui l'exécutera à l'heure dite et l'oubliera. Contrairement à cron, elle ne se
répète pas, et rien ne s'exécutera si ce démon ne tourne pas.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/

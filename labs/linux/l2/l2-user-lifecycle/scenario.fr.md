# Contexte — intégrer un nouvel utilisateur, au détail près

Un nouveau développeur arrive. Tu dois créer son compte avec des attributs
précis — le genre de tâche notée à la lettre au RHCSA : un UID fixe, un vrai
shell de connexion, un home, le bon groupe **primaire** et le bon groupe
**secondaire**.

L'idée : fixer l'identité d'un compte au moment de sa création n'est pas la même
chose que l'ajuster ensuite. Et l'erreur classique tient dans une nuance :
ajouter un groupe secondaire sans effacer ceux que l'utilisateur avait déjà.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

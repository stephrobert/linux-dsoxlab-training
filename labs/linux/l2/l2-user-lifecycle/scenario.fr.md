# Contexte — intégrer un nouvel utilisateur, au détail près

Un nouveau développeur arrive. Tu dois créer son compte avec des attributs
précis — le genre de tâche notée à la lettre au RHCSA : un UID fixe, un vrai
shell de connexion, un home, le bon groupe **primaire** et le bon groupe
**secondaire**.

Ta mission, sur la VM — crée l'utilisateur **`alice`** de sorte que :

1. son **UID** soit **1500** ;
2. son **home** soit `/home/alice` (créé) ;
3. son **shell de connexion** soit `/bin/bash` ;
4. son **groupe primaire** soit `staff` ;
5. elle appartienne aussi au **groupe secondaire** `developers`.

Crée d'abord les groupes s'ils n'existent pas. `id alice` et
`getent passwd alice` montrent le résultat.

L'idée : `useradd` fixe l'identité à la création (`-u`, `-m`, `-s`, `-g`, `-G`),
et `usermod` l'ajuste ensuite (`-aG` ajoute un groupe sans retirer les autres —
oublier `-a` est l'erreur classique).

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

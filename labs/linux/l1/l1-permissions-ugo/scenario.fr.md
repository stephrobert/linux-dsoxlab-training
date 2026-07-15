# Contexte — donner à chaque fichier les bonnes permissions

Tout dans ton répertoire de travail est lisible par tout le monde (`0644`), ce
qui est faux pour la moitié. Un secret doit rester privé, un script doit être
exécutable, une note d'équipe doit être lisible par le groupe seulement, et il
te faut un répertoire privé. Corrige les bits de permission — ni plus, ni moins
que nécessaire.

Ta mission — dans le répertoire de travail :

1. `secret.txt` → `0600` (toi seul peux le lire/écrire).
2. `deploy.sh` → `0750` (toi et le groupe pouvez l'exécuter, pas les autres).
3. `notes.txt` → `0640` (le groupe le lit, pas les autres).
4. `prive/` → un répertoire en `0700` (toi seul peux y entrer et lister).

L'idée : `chmod` pose les bits en octal (`chmod 640 fichier`) ou en symbolique
(`chmod u+x fichier`), chaque chiffre étant le triplet propriétaire/groupe/autres.
Le moindre privilège, c'est accorder exactement ce qui est nécessaire.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/

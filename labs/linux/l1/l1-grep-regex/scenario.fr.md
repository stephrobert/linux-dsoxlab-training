# Contexte — lire un journal d'accès avec grep seul

Tu as `acces.log`, dix lignes de la forme `IP - METHODE /chemin CODE`. Avec
uniquement `grep` et des expressions régulières, extrais quatre faits précis dans
des fichiers séparés : les erreurs serveur, tout ce qui n'est pas un succès, les
adresses IP distinctes, et le nombre de requêtes POST.

Ta mission — produire, dans le répertoire de travail :

1. `erreurs5xx.txt` — uniquement les lignes dont le code HTTP est un **5xx**
   (erreur serveur).
2. `sans-200.txt` — toutes les lignes **sauf** les `200` (filtre inversé).
3. `ips.txt` — les adresses IP clientes **distinctes**, triées.
4. `nb-post.txt` — le **nombre** de requêtes POST.

L'idée : une regex ancrée en fin de ligne (`$`), une classe de caractères
(`[0-9]`), le filtre inversé (`-v`), l'extraction seule (`-o`) et le comptage
(`-c`) tirent chacun un fait différent du même fichier.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/

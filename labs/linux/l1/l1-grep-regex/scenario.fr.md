# Contexte — lire un journal d'accès avec grep seul

Tu as `acces.log`, dix lignes de la forme `IP - METHODE /chemin CODE`. Avec
uniquement `grep` et des expressions régulières, extrais quatre faits précis
dans des fichiers séparés : les erreurs serveur, tout ce qui n'est pas un
succès, les adresses IP distinctes, et le nombre de requêtes POST.

L'idée : le même fichier livre quatre faits différents selon la façon dont on
l'interroge. Sélectionner des lignes, les exclure, n'extraire qu'une portion de
ligne, ou ne rendre qu'un nombre, sont quatre usages distincts d'un seul outil.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/

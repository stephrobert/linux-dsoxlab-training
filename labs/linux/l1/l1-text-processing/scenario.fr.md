# Contexte — transformer un fichier brut en faits

Tu as `ventes.csv`, huit enregistrements séparés par `;` de la forme
`date;region;produit;montant`. Avec la seule boîte à outils texte du shell,
transforme-le en quatre artefacts précis : les régions distinctes, le nombre de
ventes par région, le total général, et une version séparée par des virgules.

L'idée : chaque outil de la chaîne ne sait faire qu'une chose. Toute la
difficulté est de choisir le bon pour chaque question, et de les enchaîner dans
le bon ordre.

Méthode dans les guides compagnons :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/transformer-texte/

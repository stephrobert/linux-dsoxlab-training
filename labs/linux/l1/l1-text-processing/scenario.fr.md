# Contexte — transformer un fichier brut en faits

Tu as `ventes.csv`, huit enregistrements séparés par `;` de la forme
`date;region;produit;montant`. Avec la boîte à outils texte — `cut`, `sort`,
`uniq`, `awk`, `sed` — transforme-le en quatre artefacts précis : les régions
distinctes, le nombre de ventes par région, le total général, et une version
séparée par des virgules.

Ta mission — produire, dans le répertoire de travail :

1. `regions.txt` — les régions **distinctes**, triées.
2. `nb-par-region.txt` — le **nombre de ventes par région**.
3. `total.txt` — la **somme** de la colonne montant.
4. `en-csv.txt` — le même fichier avec `;` remplacé par `,`.

Chaque outil fait une chose : `cut` découpe une colonne, `sort -u` dédoublonne,
`uniq -c` compte les répétitions, `awk` somme un champ, `sed` réécrit un
séparateur.

Méthode dans les guides compagnons :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/traiter-texte/cut-tr-paste/

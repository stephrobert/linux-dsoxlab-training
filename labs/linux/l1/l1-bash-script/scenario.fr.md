# Contexte — un premier vrai script Bash

Un fichier de supervision liste des hôtes et leur état, un par ligne : `nom up`
ou `nom down`. Écris un script qui en tire un verdict : combien sont up, combien
down, et un code de retour qu'un pipeline peut exploiter.

Le contrat, celui que les tests vérifient : `rapport.sh`, dans le répertoire de
travail, appelé sous la forme `./rapport.sh serveurs.txt`, doit

1. lire le fichier **passé en premier argument** ;
2. afficher exactement deux lignes : `UP=<n>` et `DOWN=<n>` ;
3. **sortir avec un code non nul** quand au moins un hôte est down, `0` sinon.

Il doit commencer par un shebang et être exécutable. Les tests lancent le script
et lisent sa sortie et son code de retour ; ils le rejouent même sur un fichier
tout-up, donc le code de retour doit refléter le vrai comptage, pas une valeur
codée en dur.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/scripts-bash/premier-script/

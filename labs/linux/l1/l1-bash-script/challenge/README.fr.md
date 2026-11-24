# Un premier vrai script Bash

## La situation

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
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/scripts-bash/premier-script/

## Ce qui est demandé

### Mission

Écris `rapport.sh` dans `challenge/work/`. Il lit un fichier d'état
(`nom up` / `nom down`) passé en argument et en fait un rapport.

### Contrat de sortie

`./rapport.sh serveurs.txt` doit :

1. lire le fichier passé en `$1` ;
2. compter les UP et les DOWN (boucle + variables) ;
3. afficher exactement `UP=<n>` et `DOWN=<n>` ;
4. sortir avec un code **non nul** si au moins un hôte est down, `0` sinon.

### Contraintes

- Shebang obligatoire, script exécutable (`chmod +x rapport.sh`).
- La validation **exécute** le script (sortie + code de retour) et le rejoue sur
  un fichier tout-up : le code de retour doit dépendre du vrai comptage.

### Validation

```bash
dsoxlab check l1-bash-script
```

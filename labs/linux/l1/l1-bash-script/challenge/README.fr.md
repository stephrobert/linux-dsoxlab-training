# Challenge — l1-bash-script

## Mission

Écris `rapport.sh` dans `challenge/work/`. Il lit un fichier d'état
(`nom up` / `nom down`) passé en argument et en fait un rapport.

## Contrat de sortie

`./rapport.sh serveurs.txt` doit :

1. lire le fichier passé en `$1` ;
2. compter les UP et les DOWN (boucle + variables) ;
3. afficher exactement `UP=<n>` et `DOWN=<n>` ;
4. sortir avec un code **non nul** si au moins un hôte est down, `0` sinon.

## Contraintes

- Shebang obligatoire, script exécutable (`chmod +x rapport.sh`).
- La validation **exécute** le script (sortie + code de retour) et le rejoue sur
  un fichier tout-up : le code de retour doit dépendre du vrai comptage.

## Validation

```bash
dsoxlab check l1-bash-script
```

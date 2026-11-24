# Désigner un fichier sans se tromper

## La situation

Toute commande qui touche un fichier doit d'abord savoir où il se trouve. Deux
écritures existent pour le lui dire : l'une part de la racine et vaut depuis
n'importe où, l'autre part de l'endroit où tu te tiens et change de sens dès que
tu te déplaces. Les confondre, c'est écrire au mauvais endroit, ou ne rien
trouver du tout.

Ce lab te fait pratiquer les deux écritures sur une même copie de fichier, puis
te met à l'épreuve sur des trajets à calculer de tête, sans exécuter le moindre
shell.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/chemins-linux/

## Chemins absolus et relatifs

### Mission

Trois tâches :

1. Copie `source.txt` vers `backup/absolute/source.txt` en utilisant un **chemin absolu**.
2. Copie `source.txt` vers `backup/relative/source.txt` en utilisant un **chemin relatif**.
3. Résous les 5 énigmes de chemins de `puzzles.txt`.

### Contraintes

- Les deux copies doivent exister.
- Les réponses aux énigmes doivent être des chemins relatifs (sans `/` initial).
- Aucun placeholder ne doit subsister dans `puzzles.txt`.


### Validation

```bash
dsoxlab check l1-paths-absolute-relative
```

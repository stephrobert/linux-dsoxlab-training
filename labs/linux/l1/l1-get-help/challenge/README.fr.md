# Trouver la commande qu'on ne connaît pas

## La situation

Personne ne connaît toutes les commandes, et ce n'est pas la compétence
attendue : un système Linux embarque sa propre documentation, hors ligne, et sait
répondre aussi bien à « quelle commande fait ceci ? » qu'à « quelle option de
cette commande fait cela ? ». Savoir l'interroger vaut mieux qu'une liste apprise
par cœur.

Ce lab te met devant trois besoins exprimés en français, sur un petit fichier de
log, et te demande d'en produire le résultat. Le web est hors jeu : tout ce qu'il
te faut est déjà installé sur la machine. La validation compare tes fichiers au
contenu réel du log, nommer la bonne commande ne suffit donc pas.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/obtenir-aide/

## Trouver la bonne commande avec l'aide

Travaille dans **`challenge/work/`** — le fichier `donnees.txt` (5 lignes de log)
y a été créé par `dsoxlab run`.

---

### Mission

Personne ne connaît toutes les commandes : ce qui compte, c'est savoir **trouver
la bonne** avec `man`, `--help` et `apropos`, puis **s'en servir**. À partir de
`donnees.txt`, produis trois fichiers :

1. `fin.txt` — les **3 dernières lignes** de `donnees.txt`.
2. `compte.txt` — le **nombre de lignes** de `donnees.txt`.
3. `erreurs.txt` — uniquement les lignes contenant **`ERROR`**.

Pour chaque tâche, trouve d'abord la commande adaptée avec les outils d'aide,
puis exécute-la.

### Contraintes

- La validation compare tes fichiers au **contenu réel** de `donnees.txt` : il ne
  suffit pas de nommer la commande, il faut produire le bon résultat.

### Outils d'aide

```bash
apropos "last"        # chercher une commande par mot-clé
man tail              # les dernières lignes
man wc                # compter lignes / mots / octets
apropos "pattern"     # chercher un motif
man grep              # filtrer par motif
```

### Validation

```bash
dsoxlab check l1-get-help
```

# Challenge — l1-06 : Trouver la bonne commande avec l'aide

Travaille dans **`challenge/work/`** — le fichier `donnees.txt` (5 lignes de log)
y a été créé par `dsoxlab run`.

---

## Mission

Personne ne connaît toutes les commandes : ce qui compte, c'est savoir **trouver
la bonne** avec `man`, `--help` et `apropos`, puis **s'en servir**. À partir de
`donnees.txt`, produis trois fichiers :

1. `fin.txt` — les **3 dernières lignes** de `donnees.txt`.
2. `compte.txt` — le **nombre de lignes** de `donnees.txt`.
3. `erreurs.txt` — uniquement les lignes contenant **`ERROR`**.

Pour chaque tâche, trouve d'abord la commande adaptée avec les outils d'aide,
puis exécute-la.

## Contraintes

- La validation compare tes fichiers au **contenu réel** de `donnees.txt` : il ne
  suffit pas de nommer la commande, il faut produire le bon résultat.

## Outils d'aide

```bash
apropos "last"        # chercher une commande par mot-clé
man tail              # les dernières lignes
man wc                # compter lignes / mots / octets
apropos "pattern"     # chercher un motif
man grep              # filtrer par motif
```

## Validation

```bash
dsoxlab check l1-06-get-help
```

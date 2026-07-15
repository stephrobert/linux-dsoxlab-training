# Challenge — l1-05 : Lire une commande, puis l'utiliser

Travaille dans **`challenge/work/`** — le fichier `source.txt` (5 lignes) y a été
créé par `dsoxlab run`.

---

## Mission

Lire une commande ne suffit pas : il faut savoir la **choisir et l'utiliser**.
À partir de `source.txt`, produis trois fichiers avec la bonne commande :

1. `copie.txt` — une **copie exacte** de `source.txt` (commande `cp`).
2. `archive.tar.gz` — une **archive gzip** contenant `source.txt` (commande `tar`).
3. `numerote.txt` — `source.txt` avec un **numéro devant chaque ligne** (commande `cat`).

## Contraintes

- La validation vérifie les **fichiers réellement produits**, pas une description.
  Édite le résultat à la main et il ne collera pas : utilise les commandes.
- Ne modifie pas `source.txt`.

## Commandes utiles

```bash
cat source.txt              # lis d'abord ce que tu manipules
cp --help | head            # options de copie
tar --help | grep -A1 -- -c # créer une archive
cat --help | grep -- -n     # numéroter les lignes
```

## Validation

```bash
dsoxlab check l1-read-a-command
```

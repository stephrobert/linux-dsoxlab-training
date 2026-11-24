# Lire une ligne de commande, puis en écrire une

## La situation

Toute commande Linux suit le même schéma : le programme, ce qui modifie son
comportement, ce sur quoi il agit. Savoir lire ce schéma, c'est pouvoir
déchiffrer n'importe quelle ligne rencontrée dans une documentation, un ticket
ou un script, sans l'avoir jamais vue.

Mais lire ne suffit pas. Ce lab te demande trois résultats concrets à partir d'un
même petit fichier : une copie, une archive compressée, et une version numérotée.
À toi de composer les lignes qui les produisent. La validation regarde les
fichiers obtenus, pas ce que tu as tapé : un résultat fabriqué à la main ne
collera pas.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/anatomie-commande/

## Lire une commande, puis l'utiliser

Travaille dans **`challenge/work/`** — le fichier `source.txt` (5 lignes) y a été
créé par `dsoxlab run`.

---

### Mission

Lire une commande ne suffit pas : il faut savoir la **choisir et l'utiliser**.
À partir de `source.txt`, produis trois fichiers avec la bonne commande :

1. `copie.txt` — une **copie exacte** de `source.txt` (commande `cp`).
2. `archive.tar.gz` — une **archive gzip** contenant `source.txt` (commande `tar`).
3. `numerote.txt` — `source.txt` avec un **numéro devant chaque ligne** (commande `cat`).

### Contraintes

- La validation vérifie les **fichiers réellement produits**, pas une description.
  Édite le résultat à la main et il ne collera pas : utilise les commandes.
- Ne modifie pas `source.txt`.

### Commandes utiles

```bash
cat source.txt              # lis d'abord ce que tu manipules
cp --help | head            # options de copie
tar --help | grep -A1 -- -c # créer une archive
cat --help | grep -- -n     # numéroter les lignes
```

### Validation

```bash
dsoxlab check l1-read-a-command
```

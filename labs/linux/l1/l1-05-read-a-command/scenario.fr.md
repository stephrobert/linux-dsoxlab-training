# Lab l1-05 — Lire et décoder une commande

| | |
|---|---|
| **Niveau** | L1 — Fondamentaux (B0) |
| **Runtime** | `shell` — aucune VM requise |
| **Durée estimée** | 20 min |
| **Référence** | [Terminal Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/terminal/) |

---

## Ce que vous allez apprendre

- Identifier les trois parties de toute commande Linux : commande, options, arguments
- Distinguer les options courtes (`-l`) des options longues (`--long`)
- Comprendre ce que signifient les codes de retour `0` et non-zéro
- Repérer et corriger des erreurs de syntaxe courantes
- Utiliser `echo $?` pour lire le code de retour de la dernière commande

---

## Anatomie d'une commande

Toute commande Linux suit la même structure :

```
COMMANDE  [OPTIONS]  [ARGUMENTS]
```

| Partie | Rôle | Exemple |
|--------|------|---------|
| Commande | Le programme à exécuter | `ls`, `grep`, `find` |
| Options | Modifient le comportement | `-l`, `-a`, `--recursive` |
| Arguments | Ce sur quoi agir | `/etc`, `fichier.txt`, `"motif"` |

### Exemple 1 — `ls -la /etc`

```
ls      -la      /etc
│        │        └── argument : dossier à lister
│        └─────────── options : -l (format long) + -a (tout, y compris cachés)
└──────────────────── commande : lister le contenu d'un répertoire
```

### Exemple 2 — `grep -r "error" /var/log`

```
grep    -r       "error"   /var/log
│        │          │          └── argument : dossier où chercher
│        │          └──────────── argument : motif à rechercher
│        └─────────────────────── option : -r (récursif)
└──────────────────────────────── commande : chercher du texte dans des fichiers
```

---

## Exercice 1 — Décomposer des commandes

Pour chacune des commandes suivantes, identifiez : **COMMANDE**, **OPTIONS**, **ARGUMENTS**.

```bash
cp -r /home/bob/docs/ /backup/
cat -n /etc/passwd
find /tmp -type f -name "*.tmp"
tar -czf archive.tar.gz /var/log/
chmod 755 /usr/local/bin/myscript.sh
```

---

## Exercice 2 — Codes de retour

Toute commande retourne un **code de retour** quand elle termine :

- `0` = succès
- Toute autre valeur = erreur (la signification dépend de la commande)

Testez :

```bash
ls /etc          # réussit
echo $?          # affiche 0

ls /nexiste-pas   # échoue
echo $?           # affiche une valeur non-nulle (ex. 2)
```

---

## Exercice 3 — Trouver et corriger des commandes cassées

Les commandes suivantes sont incorrectes. Exécutez-les, lisez le message d'erreur, puis corrigez.

```bash
# 1 — Lister /etc en format long avec les fichiers cachés
ls -la /et         # cassée — qu'est-ce qui ne va pas ?

# 2 — Compter les lignes de /etc/passwd
wc /etc/paswd      # cassée — qu'est-ce qui ne va pas ?

# 3 — Afficher les 5 dernières lignes de /etc/os-release
tail -n5 /etc/os-releases   # cassée — qu'est-ce qui ne va pas ?
```

---

## Remplir le modèle

```bash
cat challenge/work/analyse.txt
nano challenge/work/analyse.txt
```

Ensuite validez :

```bash
dsoxlab check l1-05-read-a-command
```

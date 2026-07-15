# Challenge — l1-07 : Se repérer dans l'arborescence (FHS)

Travaille dans **`challenge/work/`** — le fichier `fhs.txt` y a été créé par
`dsoxlab run`.

---

## Mission

La FHS (Filesystem Hierarchy Standard) dit où chaque chose vit sous Linux. Mets
cette connaissance à l'épreuve : **localise quatre éléments réels** sur ta
machine et donne leur chemin absolu dans `fhs.txt`.

1. `LS_PATH` — le chemin absolu de la commande `ls` (via `which ls`).
2. `USER_DB` — le fichier qui liste les comptes utilisateurs locaux.
3. `LOG_DIR` — le répertoire des journaux système.
4. `HOME_PARENT` — le répertoire parent des dossiers personnels.

## Contraintes

- Chaque chemin doit **exister réellement à l'endroit attendu** : la validation
  le vérifie sur ta machine. Un chemin inventé ou mal placé échoue.
- Tous les placeholders `VOTRE_RÉPONSE_ICI` doivent être remplacés.

## Commandes utiles

```bash
which ls
ls -l /etc/passwd
ls -d /var/log
ls -d /home
```

## Validation

```bash
dsoxlab check l1-linux-filesystem
```

> Le **rôle** de chaque branche de l'arborescence (`/etc`, `/var`, `/usr`,
> `/dev`, `/tmp`…) est expliqué dans le cours et vérifié par le quiz. Ce lab,
> lui, prouve que tu sais retrouver ces emplacements sur un vrai système.

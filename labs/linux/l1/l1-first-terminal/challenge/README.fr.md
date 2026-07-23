# Challenge — l1-04 : Premiers pas dans le terminal

## Mission

Le fichier `challenge/work/premiers-pas.txt` **existe déjà** : il contient les
quatre clés et leurs placeholders. **Édite-le** (avec `nano`, `vim` ou ton
éditeur) pour y reporter les quatre valeurs réelles de ta machine. Ne le recrée
pas avec une redirection `>`, tu effacerais les clés que la validation cherche.

N'invente rien, ne devine pas : lance les commandes et reporte la sortie réelle.

## Contraintes

- **Les quatre champs doivent être remplis** : `USER`, `MACHINE`, `HOME`, `DATE`.
- **Aucun placeholder ne doit subsister** : chaque `VOTRE_RÉPONSE_ICI` doit être remplacé.
- `DATE` doit être la sortie de la commande `date` (n'importe quel format raisonnable).
- `HOME` doit être un chemin commençant par `/`.

## Structure attendue du fichier

```
USER: <value>
MACHINE: <value>
HOME: <value>
DATE: <value>
```

## Commandes utiles

- `whoami` → nom de l'utilisateur courant
- `hostname` → nom de la machine
- `echo $HOME` → répertoire personnel
- `date` → date et heure courantes

## Validation

```bash
dsoxlab check l1-first-terminal
```

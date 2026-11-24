# La première fenêtre de terminal

## La situation

Un terminal s'ouvre et n'affiche presque rien : une ligne d'invite et un curseur
qui clignote. Cette ligne dit pourtant déjà qui tu es, sur quelle machine et où
tu te trouves, et le shell qui se tient derrière connaît un certain nombre
d'autres choses sur ta session, à condition de savoir les lui demander.

Ce lab te fait relever quatre de ces valeurs sur ta propre machine : qui tu es,
comment s'appelle la machine, où est ton répertoire personnel, et quelle heure il
est pour le système. N'invente rien et ne devine rien : la validation compare tes
réponses à l'état réel de la session.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/prompt-terminal/

## Premiers pas dans le terminal

### Mission

Le fichier `challenge/work/premiers-pas.txt` **existe déjà** : il contient les
quatre clés et leurs placeholders. **Édite-le** (avec `nano`, `vim` ou ton
éditeur) pour y reporter les quatre valeurs réelles de ta machine. Ne le recrée
pas avec une redirection `>`, tu effacerais les clés que la validation cherche.

N'invente rien, ne devine pas : lance les commandes et reporte la sortie réelle.

### Contraintes

- **Les quatre champs doivent être remplis** : `USER`, `MACHINE`, `HOME`, `DATE`.
- **Aucun placeholder ne doit subsister** : chaque `<value>` doit être remplacé.
- `DATE` doit être la sortie de la commande `date` (n'importe quel format raisonnable).
- `HOME` doit être un chemin commençant par `/`.

### Structure attendue du fichier

```
USER: <value>
MACHINE: <value>
HOME: <value>
DATE: <value>
```

### Commandes utiles

- `whoami` → nom de l'utilisateur courant
- `hostname` → nom de la machine
- `echo $HOME` → répertoire personnel
- `date` → date et heure courantes

### Validation

```bash
dsoxlab check l1-first-terminal
```

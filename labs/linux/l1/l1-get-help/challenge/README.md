# Challenge — l1-06: Find the right command with help

Work in **`challenge/work/`** — the file `donnees.txt` (5 log lines)
was created there by `dsoxlab run`.

---

## Mission

Nobody knows every command: what matters is knowing how to **find
the right one** with `man`, `--help` and `apropos`, then **use it**. From
`donnees.txt`, produce three files:

1. `fin.txt` — the **last 3 lines** of `donnees.txt`.
2. `compte.txt` — the **number of lines** in `donnees.txt`.
3. `erreurs.txt` — only the lines containing **`ERROR`**.

For each task, first find the right command with the help tools,
then run it.

## Constraints

- Validation compares your files against the **real content** of `donnees.txt`: it is not
  enough to name the command, you must produce the correct result.

## Help tools

```bash
apropos "last"        # chercher une commande par mot-clé
man tail              # les dernières lignes
man wc                # compter lignes / mots / octets
apropos "pattern"     # chercher un motif
man grep              # filtrer par motif
```

## Validation

```bash
dsoxlab check l1-get-help
```

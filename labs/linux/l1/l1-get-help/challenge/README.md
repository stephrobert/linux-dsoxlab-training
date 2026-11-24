# Finding the command you do not know

## The situation

Nobody knows every command, and that is not the expected skill: a Linux system
ships its own documentation, offline, and can answer both "which command does
this?" and "which option of this command does that?". Knowing how to question it
beats any memorised list.

This lab puts three plain-language needs in front of you, on a small log file,
and asks you to produce the result. The web is out of play: everything you need
is already installed on the machine. Validation compares your files to the real
content of the log, so naming the right command is not enough.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/discover-linux/getting-help/

## Find the right command with help

Work in **`challenge/work/`** — the file `donnees.txt` (5 log lines)
was created there by `dsoxlab run`.

---

### Mission

Nobody knows every command: what matters is knowing how to **find
the right one** with `man`, `--help` and `apropos`, then **use it**. From
`donnees.txt`, produce three files:

1. `fin.txt` — the **last 3 lines** of `donnees.txt`.
2. `compte.txt` — the **number of lines** in `donnees.txt`.
3. `erreurs.txt` — only the lines containing **`ERROR`**.

For each task, first find the right command with the help tools,
then run it.

### Constraints

- Validation compares your files against the **real content** of `donnees.txt`: it is not
  enough to name the command, you must produce the correct result.

### Help tools

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

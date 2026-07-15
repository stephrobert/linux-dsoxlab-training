# Lab l1-04 — First steps in the terminal

| | |
|---|---|
| **Level** | L1 — Fundamentals (B0) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 15 min |
| **Reference** | [Terminal Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/terminal/) |

---

## What you will learn

- Identify the current user with `whoami`
- Display the home directory path using an environment variable
- Display the current date and time
- Redirect command output to a file with `>`
- Append output to an existing file with `>>`

---

## Command reference

| Command | What it does |
|---------|--------------|
| `whoami` | Prints the current username |
| `hostname` | Prints the machine hostname |
| `echo $HOME` | Prints the home directory path from the environment |
| `date` | Prints the full date and time |
| `echo "text" > file.txt` | Writes text to a file (overwrites if exists) |
| `echo "text" >> file.txt` | Appends text to a file (does not overwrite) |
| `cat file.txt` | Displays file contents |

---

## Exercise 1 — Who am I?

```bash
whoami
```

This command prints the username of the currently logged-in user.
On a shared server you may not always be the same user — this confirms who you are.

```bash
id
```

`id` shows your user ID (uid), primary group (gid), and all supplementary groups.

---

## Exercise 2 — Where am I?

```bash
hostname
echo $HOME
pwd
```

`$HOME` is an **environment variable**: a named value that the shell keeps for you.
It always holds the path to your home directory.

```bash
echo $USER    # same as whoami but from an environment variable
env           # display all environment variables
```

---

## Exercise 3 — What time is it?

```bash
date
date +"%Y-%m-%d"          # ISO date only
date +"%H:%M:%S"          # time only
date +"%Y-%m-%d %H:%M"    # combined
```

---

## Exercise 4 — Write output to a file

The `>` operator redirects what a command prints to a file instead of the screen.
If the file already exists, it is **overwritten**.

```bash
echo "something" > premiers-pas.txt
cat premiers-pas.txt
```

The `>>` operator **appends** to the file without overwriting:

```bash
echo "first line" > premiers-pas.txt
echo "second line" >> premiers-pas.txt
cat premiers-pas.txt
```

---

## Fill in the template

Open the template and capture the real values from your machine:

```bash
cat challenge/work/premiers-pas.txt   # read the template
nano challenge/work/premiers-pas.txt  # fill it in
```

Or use redirections directly:

```bash
# Example (do not copy-paste blindly — adapt to your machine):
# sed -i "s/VOTRE_RÉPONSE_ICI_USER/$(whoami)/" challenge/work/premiers-pas.txt
```

Then validate:

```bash
dsoxlab check l1-first-terminal
```

# The first terminal window

## The situation

A terminal opens and shows almost nothing: a prompt line and a blinking cursor.
That line already tells you who you are, on which machine and where you stand,
and the shell behind it knows a number of other things about your session,
provided you know how to ask.

This lab has you record four of those values on your own machine: who you are,
what the machine is called, where your home directory is, and what time it is for
the system. Do not invent, do not guess: validation compares your answers to the
real state of the session.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/discover-linux/terminal-prompt/

## First steps in the terminal

### Mission

The file `challenge/work/premiers-pas.txt` **already exists**: it holds the four
keys and their placeholders. **Edit it** (with `nano`, `vim` or your editor) to
fill in the four real values from your machine. Do not recreate it with a `>`
redirection, you would wipe the keys the validation looks for.

Do not invent or guess — run the commands and put the actual output.

### Constraints

- **All four fields must be filled**: `USER`, `MACHINE`, `HOME`, `DATE`.
- **No placeholder left**: every `<value>` must be replaced.
- `DATE` must be the output of the `date` command (any reasonable format).
- `HOME` must be a path starting with `/`.

### Expected file structure

```
USER: <value>
MACHINE: <value>
HOME: <value>
DATE: <value>
```

### Useful commands

- `whoami` → current username
- `hostname` → machine name
- `echo $HOME` → home directory
- `date` → current date and time

### Validation

```bash
dsoxlab check l1-first-terminal
```

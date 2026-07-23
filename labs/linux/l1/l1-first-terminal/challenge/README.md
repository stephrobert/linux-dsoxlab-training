# Challenge — l1-04: First steps in the terminal

## Mission

The file `challenge/work/premiers-pas.txt` **already exists**: it holds the four
keys and their placeholders. **Edit it** (with `nano`, `vim` or your editor) to
fill in the four real values from your machine. Do not recreate it with a `>`
redirection, you would wipe the keys the validation looks for.

Do not invent or guess — run the commands and put the actual output.

## Constraints

- **All four fields must be filled**: `USER`, `MACHINE`, `HOME`, `DATE`.
- **No placeholder left**: every `VOTRE_RÉPONSE_ICI` must be replaced.
- `DATE` must be the output of the `date` command (any reasonable format).
- `HOME` must be a path starting with `/`.

## Expected file structure

```
USER: <value>
MACHINE: <value>
HOME: <value>
DATE: <value>
```

## Useful commands

- `whoami` → current username
- `hostname` → machine name
- `echo $HOME` → home directory
- `date` → current date and time

## Validation

```bash
dsoxlab check l1-first-terminal
```

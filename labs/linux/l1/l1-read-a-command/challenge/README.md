# Challenge — l1-05 : Read a command, then use it

Work in **`challenge/work/`** — the `source.txt` file (5 lines) was created there
by `dsoxlab run`.

---

## Mission

Reading a command is not enough: you have to be able to **choose and use it**.
From `source.txt`, produce three files with the right command:

1. `copie.txt` — an **exact copy** of `source.txt` (`cp` command).
2. `archive.tar.gz` — a **gzip archive** containing `source.txt` (`tar` command).
3. `numerote.txt` — `source.txt` with a **number in front of each line** (`cat` command).

## Constraints

- Validation checks the **files actually produced**, not a description.
  Edit the result by hand and it won't match: use the commands.
- Do not modify `source.txt`.

## Useful commands

```bash
cat source.txt              # read what you are working with first
cp --help | head            # copy options
tar --help | grep -A1 -- -c # create an archive
cat --help | grep -- -n     # number the lines
```

## Validation

```bash
dsoxlab check l1-read-a-command
```

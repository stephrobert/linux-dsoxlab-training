# Knowing where Linux keeps its things

## The situation

On an unfamiliar machine, the real question is never "what is this file called?"
but "where is it supposed to be?". Linux answers with a convention, the **FHS**,
which every distribution follows: each kind of file has its place, and whoever
knows the plan finds it first time.

This lab does not ask you to recite the map. It asks you to locate four real
places on your machine and give their absolute path. Validation checks that each
one truly exists where you claim it does.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/navigate-filesystem/filesystem-hierarchy/

## Find your way around the tree (FHS)

Work in **`challenge/work/`** — the file `fhs.txt` was created there by
`dsoxlab run`.

---

### Mission

The FHS (Filesystem Hierarchy Standard) says where each thing lives under Linux. Put
that knowledge to the test: **locate four real items** on your
machine and give their absolute path in `fhs.txt`.

1. `LS_PATH` — the absolute path of the `ls` command (via `which ls`).
2. `USER_DB` — the file that lists the local user accounts.
3. `LOG_DIR` — the system logs directory.
4. `HOME_PARENT` — the parent directory of the personal folders.

### Constraints

- Each path must **actually exist at the expected location**: validation
  checks it on your machine. An invented or misplaced path fails.
- All `<value>` placeholders must be replaced.

### Useful commands

```bash
which ls
ls -l /etc/passwd
ls -d /var/log
ls -d /home
```

### Validation

```bash
dsoxlab check l1-linux-filesystem
```

> The **role** of each branch of the tree (`/etc`, `/var`, `/usr`,
> `/dev`, `/tmp`…) is explained in the course and checked by the quiz. This lab
> proves that you can find these locations on a real system.

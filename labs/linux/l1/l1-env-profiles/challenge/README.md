# Challenge — l1-env-profiles

## Mission

Write `env.sh` in `challenge/work/`. Once sourced, it configures
the project environment.

## Contract (after `source env.sh`)

1. `PROJET` exported = `dsoxlab`.
2. `EDITOR` exported = `vim`.
3. `GREETING` = `Bienvenue sur dsoxlab` (built from `$PROJET`).
4. `PATH` starts with `$PWD/bin`.

## Constraints

- `export` to publish the variables, `$PWD/bin` at the head of `PATH`.
- Validation **sources** your file in a subshell and launches a child to
  verify the real export. Do not touch your actual `~/.bashrc`.

## Validation

```bash
dsoxlab check l1-env-profiles
```

# Lab — environment variables & a sourced env file

> Prepare the workspace: `dsoxlab run l1-env-profiles`

## Recap

[**Environment variables on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/)

`NAME=value` sets a shell variable; `export NAME` publishes it so child processes
inherit it. `source file` runs a file in the *current* shell (so its `export`s
stick), unlike executing it. Prepending to `PATH`
(`export PATH="$PWD/bin:$PATH"`) makes a local directory win over system tools.

## Objectives

Write `env.sh` so that after `source env.sh`:

- `PROJET=dsoxlab` (exported);
- `EDITOR=vim` (exported);
- `GREETING="Bienvenue sur $PROJET"`;
- `PATH` starts with `$PWD/bin`.

## Validate

```bash
dsoxlab check l1-env-profiles
```

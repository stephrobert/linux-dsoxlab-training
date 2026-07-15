# Lab — a first Bash script

> Prepare the workspace: `dsoxlab run l1-bash-script`

## Recap

[**Write your first script on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/scripts-bash/premier-script/)

A script starts with a shebang (`#!/usr/bin/env bash`) and must be executable
(`chmod +x`). `$1` is the first argument. A `while read` loop walks a file line by
line, variables accumulate counts, `if` tests a condition, and `exit <n>` sets
the return code that callers check with `$?`.

## Objectives

Write `rapport.sh` so that `./rapport.sh serveurs.txt`:

- loops over the lines and counts UP / DOWN into variables;
- prints `UP=<n>` and `DOWN=<n>`;
- exits non-zero if any host is down, `0` otherwise.

## Validate

```bash
dsoxlab check l1-bash-script
```

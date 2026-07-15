# Challenge — l1-git-basics

## Mission

In `challenge/work/`, create a Git repository `monprojet/` and make it live.

## Goal (expected repository state)

1. `monprojet/` is a Git repository (`git init`).
2. At least **2 commits**.
3. `README.md` and `app.sh` are **tracked**.
4. A `feature` branch exists.
5. Working tree is **clean** (everything committed).

## Constraints

- `git init`, `git add`, `git commit`, `git branch`/`git switch -c`. No remote repository.
- Validation queries the **repository state** (log, ls-files, branch, status),
  not the commands typed.

## Validation

```bash
dsoxlab check l1-git-basics
```

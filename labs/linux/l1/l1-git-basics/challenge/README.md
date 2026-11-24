# Put a project under version control

## The situation

Start a Git repository from scratch, record two meaningful commits, and open a
branch to work on a feature without touching the main line. This is the loop you
repeat on every real project.

The tests inspect the **repository state** — commits, tracked files, branches —
not the commands you typed to get there.

If Git complains it needs an identity, set it once:
`git config user.name "You"` and `git config user.email "you@example.com"`.

Method in the companion guide:
https://www.stephane-robert.info/docs/developper/version/git/bases-git/ (in French)

## What is asked

### Mission

In `challenge/work/`, create a Git repository `monprojet/` and make it live.

### Goal (expected repository state)

1. `monprojet/` is a Git repository (`git init`).
2. At least **2 commits**.
3. `README.md` and `app.sh` are **tracked**.
4. A `feature` branch exists.
5. Working tree is **clean** (everything committed).

### Constraints

- `git init`, `git add`, `git commit`, `git branch`/`git switch -c`. No remote repository.
- Validation queries the **repository state** (log, ls-files, branch, status),
  not the commands typed.

### Validation

```bash
dsoxlab check l1-git-basics
```

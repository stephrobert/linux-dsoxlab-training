# Lab — Git basics

> Prepare the workspace: `dsoxlab run l1-git-basics`

## Recap

[**Git basics on the companion guide**](https://blog.stephane-robert.info/docs/developper/version/git/bases-git/)

`git init` creates a repository, `git add <file>` stages changes, `git commit -m`
records a snapshot, `git log` shows history, and `git switch -c <name>` (or
`git branch <name>`) opens a branch. `git status` tells you what is still
uncommitted.

## Objectives

In the work directory, build `monprojet/`:

- a Git repo with **≥ 2 commits**;
- tracking `README.md` and `app.sh`;
- with a `feature` branch;
- a clean working tree.

## Validate

```bash
dsoxlab check l1-git-basics
```

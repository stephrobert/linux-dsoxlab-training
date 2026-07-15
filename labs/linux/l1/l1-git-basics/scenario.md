# Context — put a project under version control

Start a Git repository from scratch, record two meaningful commits, and open a
branch to work on a feature without touching the main line. This is the loop you
repeat on every real project.

Your mission — in the work directory, create a repo `monprojet/` such that:

1. it is a Git repository (`git init`);
2. it has **at least two commits**;
3. two files are tracked: `README.md` and `app.sh`;
4. a branch named `feature` exists;
5. the working tree is **clean** (nothing left uncommitted).

The point: `git init` creates the repo, `git add` stages, `git commit` records,
`git branch` / `git switch -c` opens a line of work. The tests inspect the
repository state — commits, tracked files, branches — not the commands you typed.

If Git complains it needs an identity, set it once:
`git config user.name "You"` and `git config user.email "you@example.com"`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/developper/version/git/bases-git/

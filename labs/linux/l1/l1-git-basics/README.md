# Lab — Git basics

## Reminder

[**Git basics on the companion guide**](https://blog.stephane-robert.info/docs/developper/version/git/bases-git/)

`git init` creates a repository, `git add <file>` stages changes, `git commit -m`
records a snapshot, `git log` shows history, and `git switch -c <name>` (or
`git branch <name>`) opens a branch. `git status` tells you what is still
uncommitted.

## The course

The examples below build a demonstration repository `carnet-demo/` with its own
files and its own branch: the challenge will ask you for another repository,
other files and another branch. The point is to learn the cycle, not to copy a
line.

All the output shown here was produced on an AlmaLinux 10 with **Git 2.52.0**
and `LANG=en_US.UTF-8`. Two things vary from one machine to another and will
differ on yours: the **commit hashes** (each commit gets a different one) and
the **language of the messages**, Git being translated when the locale is.

### Check that Git is there, and which one

Git is not always installed: on a fresh machine, the command simply does not
exist.

```bash
git --version
```

```text
bash: git: command not found
```

On a RHEL-family distribution (AlmaLinux, Rocky, Fedora), the package is
installed with `dnf`:

```bash
sudo dnf install git
```

On Debian and Ubuntu, the guide gives the `apt` equivalent:

```bash
sudo apt update
sudo apt install git
```

Once installed, run the check again:

```bash
git --version
```

```text
git version 2.52.0
```

> **Look at this number before following a tutorial.** `git switch` and
> `git restore`, used below, only appeared in **Git 2.23** (August 2019). On an
> older machine, you have to fall back on `git checkout`.

### Create the repository with `git init`

`git init <name>` creates the directory if it does not exist and installs the
versioning machinery in it:

```bash
git init carnet-demo
cd carnet-demo
```

```text
hint: Using 'master' as the name for the initial branch. This default branch name
hint: will change to "main" in Git 3.0. To configure the initial branch name
hint: to use in all of your new repositories, which will suppress this warning,
hint: call:
hint:
hint: 	git config --global init.defaultBranch <name>
hint:
hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
hint: 'development'. The just-created branch can be renamed via this command:
hint:
hint: 	git branch -m <name>
hint:
hint: Disable this message with "git config set advice.defaultBranchName false"
Initialized empty Git repository in /home/ansible/carnet-demo/.git/
```

Two lessons in this output.

The last line confirms the creation. The `hint:` lines are **not an error**:
Git warns that the initial branch is called `master` for lack of an
`init.defaultBranch` setting, and announces that this default will become
`main` in Git 3.0. The two names are functionally identical. Above all,
remember that a brand new repository does **not necessarily** have the branch
you think: ask rather than assume.

```bash
git branch --show-current
```

```text
master
```

The directory that was created is empty, with one detail:

```bash
ls -a
```

```text
.
..
.git
```

The whole of Git lives in this `.git/`. Deleting it destroys the history.

```bash
ls -la .git/
```

```text
total 16
drwxr-xr-x. 6 ansible ansible  103 Jul 22 13:57 .
drwxr-xr-x. 3 ansible ansible   18 Jul 22 13:57 ..
-rw-r--r--. 1 ansible ansible   92 Jul 22 13:57 config
-rw-r--r--. 1 ansible ansible   73 Jul 22 13:57 description
-rw-r--r--. 1 ansible ansible   23 Jul 22 13:57 HEAD
drwxr-xr-x. 2 ansible ansible 4096 Jul 22 13:57 hooks
drwxr-xr-x. 2 ansible ansible   21 Jul 22 13:57 info
drwxr-xr-x. 4 ansible ansible   30 Jul 22 13:57 objects
drwxr-xr-x. 4 ansible ansible   31 Jul 22 13:57 refs
```

| Item | Role |
|---|---|
| `HEAD` | points to the current branch |
| `config` | configuration specific to this repository (`--local` level) |
| `objects/` | all the Git objects: commits, trees, file contents |
| `refs/` | the branch and tag pointers |
| `hooks/` | scripts triggered automatically on certain events |
| `info/` | local exclusions and miscellaneous information |

`HEAD` is only a one-line text file:

```bash
cat .git/HEAD
```

```text
ref: refs/heads/master
```

Finally, the state of a repository without any commit:

```bash
git status
```

```text
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

At this point, `git branch` returns **nothing at all**: the branch will only
really exist at the first commit, since a branch is a pointer and there is
nothing to point at yet.

### The daily cycle: edit, stage, commit

The guide sums up the whole of Git in one diagram:

```text
   Edit       →      Stage       →      Commit       →     Verify
 (editor)         (git add)         (git commit)         (git log)
```

Create a file, then ask for its state:

```bash
printf 'Carnet de bord de l atelier\n' > notes.txt
git status
```

```text
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	notes.txt

nothing added to commit but untracked files present (use "git add" to track)
```

`notes.txt` is **untracked**: Git sees it but does not deal with it. The short
form says the same thing in one line:

```bash
git status -s
```

```text
?? notes.txt
```

Two columns: the left one for the index, the right one for the working
directory. `??` flags a file unknown to Git, `A` a staged addition, `M` a
modification.

`git add` moves the file into the index, the antechamber of the next commit:

```bash
git add notes.txt
git status -s
```

```text
A  notes.txt
```

The `A` is in the left column: the content is staged, ready to be recorded.

### Identity: Git refuses to commit without it

A commit carries the name and address of its author. Without them, the command
fails:

```bash
git commit -m "Add the logbook"
```

```text
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: empty ident name (for <ansible@atelier.lab>) not allowed
```

Git configuration has three levels, from the broadest to the most specific, the
most specific winning:

| Level | Scope | File | Option |
|---|---|---|---|
| system | all users of the machine | `/etc/gitconfig` | `--system` |
| global | your account | `~/.gitconfig` | `--global` |
| local | this repository only | `.git/config` | `--local` |

Without an option, `git config` writes at the **local** level, which is exactly
what an exercise repository needs: nothing spills over onto the rest of the
machine.

```bash
git config user.name "Etudiant Demo"
git config user.email "etudiant@example.lab"
git config --list --show-origin | grep user
```

```text
file:.git/config	user.name=Etudiant Demo
file:.git/config	user.email=etudiant@example.lab
```

`--show-origin` tells you which file each value comes from: it is the fastest
way to understand why a setting is not the one you thought.

The commit now goes through:

```bash
git commit -m "Add the logbook"
```

```text
[master (root-commit) fc9cf0e] Add the logbook
 1 file changed, 1 insertion(+)
 create mode 100644 notes.txt
```

This line reads as follows: branch `master`, `root-commit` because it is the
very first commit of the repository (it has no parent), `fc9cf0e` the
abbreviated hash, then the message. On your machine the hash will be different:
it depends on the content, the author and the date.

```bash
git status
```

```text
On branch master
nothing to commit, working tree clean
```

### Excluding what must not be versioned

The `.gitignore` file lists what Git must ignore. It is created **before** the
first commit, not after.

```bash
printf 'verifier les sauvegardes\nrelire le journal\n' > taches.txt
printf 'sortie temporaire\n' > sortie.log
printf '*.log\n' > .gitignore
git status -s
```

```text
?? .gitignore
?? taches.txt
```

`sortie.log` has disappeared from the list: the `*.log` pattern excludes it.
A few common patterns:

| Pattern | Matches |
|---|---|
| `*.log` | every file ending in `.log` |
| `build/` | the `build` directory and all its content |
| `/TODO` | only the `TODO` file at the root of the repository |
| `!important.log` | exception: track this file despite `*.log` |

> **Never commit a secret.** Passwords, API keys, tokens, certificates: once in
> the history, they stay there, visible to everyone with access to the
> repository, even if deleted afterwards. The `.gitignore` is the first
> barrier.

Before committing, inspect what is about to be recorded:

```bash
git add taches.txt .gitignore
git diff --staged
```

```text
diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..397b4a7
--- /dev/null
+++ b/.gitignore
@@ -0,0 +1 @@
+*.log
diff --git a/taches.txt b/taches.txt
new file mode 100644
index 0000000..d556b71
--- /dev/null
+++ b/taches.txt
@@ -0,0 +1,2 @@
+verifier les sauvegardes
+relire le journal
```

| Command | Compares | Shows |
|---|---|---|
| `git diff` | working directory and index | what is not staged yet |
| `git diff --staged` | index and last commit | what will be committed |
| `git diff HEAD` | working directory and last commit | everything that changed |

```bash
git commit -m "Add the task list and the gitignore"
```

```text
[master bc410a8] Add the task list and the gitignore
 2 files changed, 3 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 taches.txt
```

### Reading the history

```bash
git log
```

```text
commit bc410a8e63207e4a2fbd49a2806c9f7e6cc5203b
Author: Etudiant Demo <etudiant@example.lab>
Date:   Wed Jul 22 13:58:17 2026 +0000

    Add the task list and the gitignore

commit fc9cf0e0c61b9d8f91ac5905df9ad0e8e1e75aeb
Author: Etudiant Demo <etudiant@example.lab>
Date:   Wed Jul 22 13:58:11 2026 +0000

    Add the logbook
```

From the most recent to the oldest. On a long history, the output goes through
a pager: `q` to leave it.

The everyday view fits on one line per commit:

```bash
git log --oneline
```

```text
bc410a8 Add the task list and the gitignore
fc9cf0e Add the logbook
```

> **Where are the `(HEAD -> master)` of the tutorials?** Git only decorates the
> output when it goes to a terminal. In a pipe or a redirection, the decoration
> disappears. Add `--decorate` to force it:
> `git log --oneline --decorate` displays
> `bc410a8 (HEAD -> master) Add the task list and the gitignore`.

To find out which files each commit touched:

```bash
git log --stat --oneline
```

```text
bc410a8 Add the task list and the gitignore
 .gitignore | 1 +
 taches.txt | 2 ++
 2 files changed, 3 insertions(+)
fc9cf0e Add the logbook
 notes.txt | 1 +
 1 file changed, 1 insertion(+)
```

`git show` details a given commit, `--stat` limits the display to the files:

```bash
git show --stat HEAD
```

```text
commit bc410a8e63207e4a2fbd49a2806c9f7e6cc5203b
Author: Etudiant Demo <etudiant@example.lab>
Date:   Wed Jul 22 13:58:17 2026 +0000

    Add the task list and the gitignore

 .gitignore | 1 +
 taches.txt | 2 ++
 2 files changed, 3 insertions(+)
```

Other useful filters, taken from the guide: `git log --author="name"`,
`git log --since="2 weeks ago"`, `git log -- path/file`,
`git log --grep="word"` and `git log -S "text"`, which finds the commit that
introduced or removed a piece of code.

Finally, the list of the files actually **tracked**, which is not the same
thing as the list of the files present on disk:

```bash
git ls-files
```

```text
.gitignore
notes.txt
taches.txt
```

### Opening a branch

A branch is a movable pointer to a commit. Nothing is copied:

```bash
git branch brouillon
ls -l .git/refs/heads/
```

```text
total 8
-rw-r--r--. 1 ansible ansible 41 Jul 22 13:58 brouillon
-rw-r--r--. 1 ansible ansible 41 Jul 22 13:58 master
```

41 bytes each: the 40-character commit hash, plus the newline. That is all a
branch is.

`git branch <name>` creates the pointer **without** switching to it. The
asterisk marks the current branch:

```bash
git branch
```

```text
  brouillon
* master
```

To go there:

```bash
git switch brouillon
```

```text
Switched to branch 'brouillon'
```

```bash
git branch --show-current
cat .git/HEAD
```

```text
brouillon
ref: refs/heads/brouillon
```

`HEAD` followed: it always designates where you are.

Both steps fit in one command, `-c` for create:

```bash
git switch -c essai
```

```text
Switched to a new branch 'essai'
```

> **`switch` or `checkout`?** `git switch -c <name>` and
> `git checkout -b <name>` do the same thing. `git checkout` is the historical
> syntax, but it also serves to restore files, which is confusing. Since Git
> 2.23, `git switch` only changes branch.

What is committed on one branch does not move the other. A commit made from
`brouillon` advances that pointer only:

```bash
git log --oneline --graph --all --decorate
```

```text
* f9b38b3 (HEAD -> brouillon) Note an idea to dig into
* bc410a8 (master) Add the task list and the gitignore
* fc9cf0e Add the logbook
```

`--all` shows every branch, `--graph` draws their shape. Back on `master`, the
file modified in `brouillon` has recovered its earlier content: that is the
whole point of a branch, isolating a piece of work.

Deleting a merged branch is immediate, deleting a branch that carries unique
work is refused:

```bash
git switch master
git branch -d essai
```

```text
Switched to branch 'master'
Deleted branch essai (was bc410a8).
```

```bash
git branch -d brouillon
```

```text
error: the branch 'brouillon' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D brouillon'
```

This refusal is a protection: `-D` forces it and loses the commits that exist
nowhere else.

### Knowing whether the working tree is clean

"Clean" has a precise meaning: nothing modified, nothing staged and waiting, no
file untracked and not ignored. The script-readable form is
`git status --porcelain`, whose output is **empty** when everything is
recorded.

With one modification and one new file waiting:

```bash
git status --porcelain
```

```text
 M taches.txt
?? memo.txt
```

The first line starts with a space: the left column (the index) is empty, only
the working directory has changed. Once both files have been dealt with, the
same command displays nothing at all any more, not even an empty line. It is
this null output that defines a clean tree.

Note that `git commit -am "..."` only stages the files **already tracked**: a
new file would stay at `??`, so the tree would stay dirty. For a new file, you
have to go through `git add`.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `fatal: not a git repository (or any of the parent directories): .git` | you are not in the repository: `cd` into it, or `git init` if it does not exist |
| `bash: git: command not found` | the package is not installed (`sudo dnf install git` or `sudo apt install git`) |
| `fatal: empty ident name ... not allowed` | identity missing: `git config user.name` and `git config user.email` in the repository |
| `fatal: your current branch 'master' does not have any commits yet` | the repository has no commit yet: `git add` then `git commit` |
| `git add` ignores a file | it matches a `.gitignore` pattern: check it, or force with `git add -f` |
| `git diff` shows nothing although you made a change | the changes are already staged: `git diff --staged` |
| `error: the branch 'x' is not fully merged` | the branch carries commits absent elsewhere: `-D` to force, knowingly |
| `git init` answers `Reinitialized existing Git repository` | the directory is already a repository: running `git init` again is harmless, but useless |
| `git branch` returns nothing | repository without any commit: the branch does not exist yet |

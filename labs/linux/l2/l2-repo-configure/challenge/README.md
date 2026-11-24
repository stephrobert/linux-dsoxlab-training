# Teach dnf about a new repository

## The situation

Software has to come from somewhere. When a package isn't in the default repos,
you have to teach `dnf` where to look, by declaring an extra repository. Do it
right: a clear id, a real `baseurl`, the repo enabled, and **GPG-checked** so
packages are verified.

The point: a repository is described in an INI-style configuration file, one
`[section]` per repo. Signature checking is the security default: you do not turn
it off to make your life easier. What remains is finding where that file belongs,
and how to make dnf confirm it picked the repo up.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/maintain/packages/dnf/

## What is asked

### Mission

Declare a `labrepo` repository under `/etc/yum.repos.d/`.

### Goal (expected state)

1. `/etc/yum.repos.d/labrepo.repo` defines a `[labrepo]` section.
2. A valid http(s) `baseurl`.
3. `enabled=1`.
4. `gpgcheck=1` (with `gpgkey`).
5. `dnf repolist --all` lists `labrepo`.

### Constraints

- INI file, one `[section]` per repository ; do not remove `gpgcheck`. The
  validation **parses the file** and queries `dnf repolist`.

### Validation

```bash
dsoxlab check l2-repo-configure
```

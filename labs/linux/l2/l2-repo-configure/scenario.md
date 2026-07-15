# Context — teach dnf about a new repository

Software has to come from somewhere. When a package isn't in the default repos,
you point `dnf` at another one by dropping a `.repo` file under
`/etc/yum.repos.d/`. Do it right: a clear id, a real `baseurl`, enabled, and
**GPG-checked** so packages are verified.

Your mission, on the VM — create `/etc/yum.repos.d/labrepo.repo` so that:

1. it defines a repo with id **`[labrepo]`**;
2. it has a valid **`baseurl`** (e.g. the AlmaLinux 10 AppStream mirror);
3. it is **`enabled=1`**;
4. it is **`gpgcheck=1`** (with a `gpgkey`), so signatures are verified.

Confirm with `dnf repolist` that dnf now knows the repo.

The point: a `.repo` file is INI — one `[section]` per repo. `gpgcheck=1` is the
security default you should never drop; `dnf repolist` (and `--all`) lists what
dnf has configured.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

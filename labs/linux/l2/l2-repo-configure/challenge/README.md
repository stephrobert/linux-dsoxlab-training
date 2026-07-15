# Challenge — l2-repo-configure

## Mission

Declare a `labrepo` repository under `/etc/yum.repos.d/`.

## Goal (expected state)

1. `/etc/yum.repos.d/labrepo.repo` defines a `[labrepo]` section.
2. A valid http(s) `baseurl`.
3. `enabled=1`.
4. `gpgcheck=1` (with `gpgkey`).
5. `dnf repolist --all` lists `labrepo`.

## Constraints

- INI file, one `[section]` per repository ; do not remove `gpgcheck`. The
  validation **parses the file** and queries `dnf repolist`.

## Validation

```bash
dsoxlab check l2-repo-configure
```

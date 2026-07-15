# Challenge — l1-02: Recognize your distribution's ecosystem

Work in **`challenge/work/`** — the file `choix-distro.txt` was created there
by `dsoxlab run`.

---

## Mission

Every distribution family has its ecosystem: family, package
manager, commands. Before installing anything, you must know
**which one you are using**. Identify your machine's real ecosystem and record
three values in `choix-distro.txt`:

1. `FAMILY` — your distribution's family (`debian`, `rhel`, `suse`, `arch`,
   `alpine`), inferred from `/etc/os-release`.
2. `PACKAGE_MANAGER` — the package manager actually present (`apt`,
   `dnf`, `zypper`, `pacman`, `apk`).
3. `INSTALL_CMD` — the command to install a package with THAT manager.

## Constraints

- Each answer must match **what your machine actually exposes**: the
  validation checks it (family via `/etc/os-release`, manager via `which`).
  An answer that does not match your machine fails.
- All `VOTRE_RÉPONSE_ICI` placeholders must be replaced.

## Useful commands

```bash
grep -E '^ID=|^ID_LIKE=' /etc/os-release
which apt ; which dnf ; which zypper ; which pacman ; which apk
```

## Validation

```bash
dsoxlab check l1-choose-distro
```

> **Choosing** a distribution based on a context (beginner, RHCSA, personal
> server) and the differences between families are covered in the course and the
> quiz. This lab proves that you can recognize your own system.

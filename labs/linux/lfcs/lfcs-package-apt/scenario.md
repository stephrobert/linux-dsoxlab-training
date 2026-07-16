# Context — Debian package management with apt

On a Debian/Ubuntu system, packages are handled by **apt** (high level) and
**dpkg** (low level). You need to install a tool, then **pin** it so a system
upgrade won't change it — and be able to say which package a given file came from.

Your mission, on the Ubuntu VM:

1. Install the **`tree`** package: `sudo apt-get install -y tree`.
2. **Hold** it so `apt upgrade` skips it: `sudo apt-mark hold tree`.
3. Be able to identify the owning package of a file:
   `dpkg -S /usr/bin/tree` returns `tree`.

The point: `apt-get install`/`remove` manage packages with dependencies,
`apt-mark hold` freezes a package's version, `apt-mark showhold` lists frozen
packages, and `dpkg -S <file>` / `dpkg -l` query what dpkg knows — the Debian
equivalents of `dnf` and `rpm -qf`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/

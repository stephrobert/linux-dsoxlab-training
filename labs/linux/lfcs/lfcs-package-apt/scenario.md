# Context — Debian package management with apt

On a Debian/Ubuntu system, packages are handled by **apt** (high level) and
**dpkg** (low level). You need to install a tool, then **pin** it so a system
upgrade won't change it — and be able to say which package a given file came from.

The point: apt manages packages with their dependencies and can freeze a
package's version so an upgrade leaves it alone; dpkg, underneath, can tell which
package a file belongs to. These are the Debian counterparts of `dnf` and `rpm`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/

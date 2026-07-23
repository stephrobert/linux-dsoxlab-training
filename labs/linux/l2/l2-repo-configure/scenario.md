# Context — teach dnf about a new repository

Software has to come from somewhere. When a package isn't in the default repos,
you have to teach `dnf` where to look, by declaring an extra repository. Do it
right: a clear id, a real `baseurl`, the repo enabled, and **GPG-checked** so
packages are verified.

The point: a repository is described in an INI-style configuration file, one
`[section]` per repo. Signature checking is the security default: you do not turn
it off to make your life easier. What remains is finding where that file belongs,
and how to make dnf confirm it picked the repo up.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

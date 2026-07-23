# Context — bring the machine to a target software state

Managing software is daily work: install what a service needs, remove what
shouldn't be there, and be able to prove the result. Right now `zip` is installed
but unwanted, and `tree` is missing but needed.

The point: the package manager changes the machine's software state and resolves
dependencies along the way; the RPM database keeps the record. The tests read
that database, so the machine's real state is what counts, not the command you
typed.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

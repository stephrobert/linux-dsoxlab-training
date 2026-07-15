# Context — bring the machine to a target software state

Managing software is daily work: install what a service needs, remove what
shouldn't be there, and be able to prove the result. Right now `zip` is installed
but unwanted, and `tree` is missing but needed.

Your mission, on the VM:

1. **Install** the `tree` package.
2. **Remove** the `zip` package.
3. Be able to **query** the result (`rpm -q tree`, `rpm -q zip`,
   `dnf list installed`).

The point: `dnf install`/`dnf remove` change the software state and resolve
dependencies; `rpm -q` and `dnf list installed` inspect it. The tests read the
RPM database, so the machine's real state is what counts.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/

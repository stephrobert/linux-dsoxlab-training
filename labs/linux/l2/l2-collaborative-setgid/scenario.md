# Context — a shared directory that actually shares

The `devteam` group (alice, bob) needs a common directory, `/srv/partage`, where
everyone can drop files that the **whole group** can then edit. Right now it's
owned by `root:root` and every file someone creates keeps *their own* group — so
collaboration breaks. The fix is the **set-GID bit** on the directory.

The point: on a **directory**, the set-GID bit makes every new file inside
inherit the directory's group instead of the creator's primary group — the one
thing that makes a shared folder truly collaborative.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/

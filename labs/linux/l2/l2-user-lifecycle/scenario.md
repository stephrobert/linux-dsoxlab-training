# Context — onboard a new user, exactly

A new developer joins. You must create their account with precise attributes —
the kind of task graded to the letter on RHCSA: a fixed UID, a real login shell,
a home directory, the right **primary** group and the right **supplementary**
group.

Your mission, on the VM — create the user **`alice`** so that:

1. her **UID** is **1500**;
2. her **home** is `/home/alice` (created);
3. her **login shell** is `/bin/bash`;
4. her **primary group** is `staff`;
5. she is also a member of the **supplementary group** `developers`.

Create the groups first if they do not exist. `id alice` and
`getent passwd alice` show the result.

The point: `useradd` sets identity at creation (`-u`, `-m`, `-s`, `-g`, `-G`),
and `usermod` adjusts it later (`-aG` appends a group without dropping the
others — forgetting `-a` is the classic mistake).

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

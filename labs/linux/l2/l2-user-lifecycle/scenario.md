# Context — onboard a new user, exactly

A new developer joins. You must create their account with precise attributes —
the kind of task graded to the letter on RHCSA: a fixed UID, a real login shell,
a home directory, the right **primary** group and the right **supplementary**
group.

The point: pinning an account's identity when you create it is not the same as
adjusting it afterwards. And the classic mistake hangs on one nuance: adding a
supplementary group without wiping the ones the user already had.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/

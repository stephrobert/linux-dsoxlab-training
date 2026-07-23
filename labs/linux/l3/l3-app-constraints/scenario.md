# Context — raise an application's resource ceiling

The service running as **`appuser`** opens thousands of files and keeps hitting
the default open-files limit. You must raise its `nofile` limit — and make it
stick for every new session, not just this shell.

The point: what you tweak inside a shell only holds for that shell. A durable
policy is declared elsewhere and applied when each session opens. And two values
coexist: the soft limit, which is the default in force, and the hard limit, which
is the ceiling a user can raise up to.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/

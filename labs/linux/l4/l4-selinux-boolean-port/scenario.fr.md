# Contexte — SELinux est enforcing, et il dit non

SELinux est en mode **enforcing**. Une app web a besoin de deux choses que la
policy interdit par défaut : ouvrir des connexions réseau sortantes, et écouter
sur le port non standard **8404/tcp**. Tu ne vas pas désactiver SELinux, tu vas
accorder exactement ce qu'il faut, durablement.

L'idée : les booléens SELinux sont des interrupteurs de policy, et un
interrupteur basculé à chaud revient tout seul au reboot si on ne demande pas
explicitement le contraire. Les ports non standard, eux, doivent être
**étiquetés** : sans étiquette, un service confiné n'a tout simplement pas le
droit de s'y attacher.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/

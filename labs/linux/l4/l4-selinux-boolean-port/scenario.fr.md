# Contexte — SELinux est enforcing, et il dit non

SELinux est en mode **enforcing**. Une app web a besoin de deux choses que la
policy interdit par défaut : ouvrir des connexions réseau sortantes, et écouter
sur le port non standard **8404/tcp**. Tu ne vas pas désactiver SELinux — tu vas
accorder exactement ce qu'il faut, durablement.

Ta mission, sur la VM :

1. Active le booléen **`httpd_can_network_connect`**, de façon **persistante**
   (`setsebool -P`).
2. Étiquette le port **`8404/tcp`** en **`http_port_t`**
   (`semanage port -a -t http_port_t -p tcp 8404`).

L'idée : les booléens SELinux basculent des interrupteurs de policy — `-P` les
fait survivre au reboot ; sans lui ils reviennent en arrière. Les ports non
standard doivent être **étiquetés** avec `semanage port`, sinon un service confiné
ne peut pas les ouvrir. `getsebool` et `semanage port -l` lisent l'état.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/

# Contexte — régler la machine pour le débit

Cette machine fait du batch intensif en données mais reste sur le profil tuned
**`balanced`** par défaut. Bascule-la sur un profil taillé pour le **débit**,
pour que les réglages noyau (gouverneur CPU, I/O, VM) soient prévus pour une
charge soutenue, et que ça survive à un reboot.

L'idée : `tuned` regroupe des dizaines de réglages noyau et sysfs dans des
profils nommés, un par grand type de charge. Le profil retenu est enregistré sur
disque, et c'est ce qui le fait tenir aux reboots. Reste à savoir lequel choisir
et comment en changer.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/

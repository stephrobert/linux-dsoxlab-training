# Contexte — découper un disque en GPT

La machine a un disque supplémentaire, vierge : c'est celui-là, et lui seul, que
tu dois découper. Avant de porter un filesystem, un membre LVM ou un périphérique
RAID, il lui faut une **table de partition**. Les systèmes modernes utilisent
**GPT** (sans les limites du vieux MBR : 4 partitions et 2 Tio). Ta mission :
poser GPT et découper deux partitions.

L'idée : écrire une table de partition ne suffit pas à la rendre visible. Le
noyau garde sa vue de l'ancienne tant qu'on ne lui demande pas de la relire, ou
tant que la machine n'a pas redémarré.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/

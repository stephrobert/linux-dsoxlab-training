# Contexte — un paramètre noyau qui tient

Tu veux que le noyau redémarre automatiquement dix secondes après un panic
(`panic=10`) — et ça doit tenir aux reboots **et** aux mises à jour du noyau.
Éditer le `/proc/cmdline` vivant est impossible ; le paramètre a sa place dans le
**bootloader**.

L'idée : un paramètre noyau doit atteindre deux populations distinctes, les
noyaux déjà installés et ceux qui le seront demain. Rien ne garantit qu'un même
geste couvre les deux, et sur une distribution à entrées de démarrage BLS c'est
précisément là que le piège se referme.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/grub/

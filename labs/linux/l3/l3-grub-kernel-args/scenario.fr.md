# Contexte — un paramètre noyau qui tient

Tu veux que le noyau redémarre automatiquement dix secondes après un panic
(`panic=10`) — et ça doit tenir aux reboots **et** aux mises à jour du noyau.
Éditer le `/proc/cmdline` vivant est impossible ; le paramètre a sa place dans le
**bootloader**.

Ta mission, sur la VM :

1. Ajoute `panic=10` aux noyaux **existants** :
   `grubby --update-kernel=ALL --args="panic=10"`.
2. Ajoute `panic=10` à **`GRUB_CMDLINE_LINUX`** dans `/etc/default/grub` pour que
   les **futurs** noyaux (après une mise à jour) l'aient aussi.

L'idée : `grubby` édite les entrées de démarrage des noyaux installés ;
`/etc/default/grub` est le modèle que `grub2-mkconfig` utilise pour les nouveaux
noyaux — il faut les deux pour un paramètre qui persiste vraiment.
`grubby --info=DEFAULT` montre les arguments actuels du noyau par défaut.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/grub/

# Contexte — Protéger les données au repos avec LUKS

Sur **alma-rhcsa-1.lab**, un disque amovible va contenir des exports sensibles.
Si le disque quitte les locaux, son contenu doit rester illisible. Vous le
chiffrez avec **LUKS2** et le faites déverrouiller automatiquement au démarrage
via un fichier-clé.

Le disque libre à traiter est désigné dans `/root/luks-disk.env`, et la clé qui
servira à l'ouvrir est déjà déposée sur la machine.

Méthode dans le guide associé :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/

# Contexte — Protéger les données au repos avec LUKS

Sur **alma-rhcsa-1.lab**, un disque amovible va contenir des exports sensibles.
Si le disque quitte les locaux, son contenu doit rester illisible. Vous le
chiffrez avec **LUKS2** et le faites déverrouiller automatiquement au démarrage
via un fichier-clé.

Votre mission :

1. Chiffrer le disque (LUKS2) et l'ouvrir.
2. Y poser un système de fichiers et le monter.
3. Le faire déverrouiller au boot via `/etc/crypttab`.

Méthode dans le guide associé :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/

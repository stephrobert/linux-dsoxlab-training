# Contexte — découper un disque en GPT

La machine a un disque supplémentaire, vierge. Avant de porter un filesystem, un
membre LVM ou un périphérique RAID, il lui faut une **table de partition**. Les
systèmes modernes utilisent **GPT** (sans les limites du vieux MBR : 4 partitions
et 2 Tio). Ta mission : poser GPT et découper deux partitions.

Ta mission, sur la VM :

1. Poser une table **GPT** sur le disque supplémentaire (`parted ... mklabel gpt`).
2. Créer la partition 1 de **512 Mio**.
3. Créer la partition 2 de **1 Gio**.
4. Faire relire la table au noyau (`partprobe`) pour que les périphériques
   `…1` / `…2` apparaissent.

L'idée : `parted` écrit la table, et le noyau ne voit les nouvelles partitions
qu'après un `partprobe` (ou un reboot) qui la rafraîchit. `lsblk` montre le
résultat.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/

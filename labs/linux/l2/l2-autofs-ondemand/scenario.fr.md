# Contexte — monter seulement quand c'est nécessaire

Certains filesystems ne doivent pas rester montés en permanence — un disque
rarement utilisé, un partage réseau. **autofs** les monte **à l'accès** et les
démonte après un délai d'inactivité, économisant les ressources et évitant les
montages fantômes. Ici, le disque supplémentaire porte un XFS ; câble-le pour
qu'un accès à `/autofs/data` le monte.

Ta mission, sur la VM :

1. Dans une **carte maître** (`/etc/auto.master.d/lab.autofs`), rattache
   `/autofs` à une carte de montage (`/etc/auto.lab`).
2. Dans la **carte de montage** (`/etc/auto.lab`), déclare la clé `data` comme un
   montage XFS de la partition (son chemin est dans `/root/autofs-disk.env`).
3. Active et démarre **autofs**.
4. Accède à `/autofs/data` — il doit se monter automatiquement et exposer
   `marker.txt`.

L'idée : autofs ne monte rien tant que la clé n'est pas accédée ; la carte maître
dit *où*, la carte de montage dit *quoi*, et `--timeout` règle le démontage
automatique.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/

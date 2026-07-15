# Contexte — poser un vrai filesystem sur une partition

Une partition vierge attend. Une partition n'est qu'un espace réservé tant
qu'elle ne porte pas de **filesystem**. Ta mission : la formater en **XFS** (le
défaut RHEL, excellent pour les gros fichiers et la montée en charge), lui donner
un **label** pour l'identifier facilement, et la monter.

Ta mission, sur la VM :

1. Formater la partition préparée en **XFS** avec le label **`DATA`**
   (`mkfs.xfs -L DATA <part>`).
2. Créer le point de montage `/srv/xfs`.
3. **Monter** le filesystem dessus.

L'idée : `mkfs.xfs` crée le filesystem et `-L` y appose un label ; `blkid` montre
le type et le label ; un label permet de monter par `LABEL=` plutôt que par un
nom de périphérique fragile. `lsblk -f` montre le résultat.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/

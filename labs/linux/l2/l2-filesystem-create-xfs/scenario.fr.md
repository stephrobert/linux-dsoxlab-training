# Contexte — poser un vrai filesystem sur une partition

Une partition vierge attend. Une partition n'est qu'un espace réservé tant
qu'elle ne porte pas de **filesystem**. Ta mission : la formater en **XFS** (le
défaut RHEL, excellent pour les gros fichiers et la montée en charge), lui donner
un **label** pour l'identifier facilement, et la monter.

L'idée : un label est une étiquette portée par le filesystem lui-même. Il permet
de désigner ce dernier par un nom stable, plutôt que par un nom de périphérique
fragile qui peut changer d'un démarrage à l'autre.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/

# Contexte — le disque est plein

Une alerte tombe : les écritures dans `/srv/data` échouent, « No space left on
device ». Un filesystem y est presque plein. Ta mission, c'est le réflexe ops du
quotidien : trouver ce qui mange l'espace et le récupérer — **sans** effacer les
données qui comptent.

L'idée : mesurer l'occupation d'un filesystem et attribuer cette occupation aux
répertoires qui la causent, ce sont deux gestes différents. Un piège classique
(RHCSA) : quand les deux mesures se contredisent, c'est qu'un processus tient
encore un fichier supprimé mais toujours ouvert, et l'espace ne revient que
lorsqu'il le relâche. Ici, rassure-toi, le coupable est bien un fichier présent
sur le disque.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/

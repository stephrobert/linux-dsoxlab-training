# Contexte — le disque est plein

Une alerte tombe : les écritures dans `/srv/data` échouent, « No space left on
device ». Un filesystem y est presque plein. Ta mission, c'est le réflexe ops du
quotidien : trouver ce qui mange l'espace et le récupérer — **sans** effacer les
données qui comptent.

Ta mission, sur la VM :

1. Confirmer quel filesystem est plein (`df -h`).
2. Trouver le plus gros consommateur dessous (`du -h --max-depth=1 /srv/data`,
   puis creuser).
3. Supprimer le superflu (un cache boursouflé) pour faire redescendre `/srv/data`
   **sous 50 %**.
4. Conserver le fichier légitime `/srv/data/app.log`.

L'idée : `df` montre l'occupation d'un filesystem, `du` l'attribue aux
répertoires. Un piège classique (RHCSA) : si `df` dit plein mais `du` ne trouve
rien, c'est qu'un processus tient encore un fichier **supprimé mais ouvert** —
`lsof +L1` le révèle, et libérer l'espace exige que le processus le relâche. Ici
le coupable est bien sur le disque, `du` le trouvera.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/

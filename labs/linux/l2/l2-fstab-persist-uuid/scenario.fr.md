# Contexte — rendre un montage résistant au reboot

La machine a un disque supplémentaire, déjà formaté en ext4, mais il n'est ni
monté ni déclaré. Ta mission : le monter sur `/srv/data` et rendre ce montage
**permanent** : le genre de tâche qui fait échouer les candidats RHCSA quand ils
montent à la main sans rien déclarer, ou quand ils référencent le disque par un
nom de périphérique qui peut changer au prochain démarrage.

L'idée : les noms de périphériques (`/dev/vdb`) ne sont pas stables d'un reboot à
l'autre ; un UUID l'est. Reste à savoir où se déclare un montage permanent, et
comment y désigner le disque autrement que par son nom de périphérique.

Reste surtout une question que beaucoup escamotent : une fois la ligne écrite,
comment savoir qu'elle est bonne **avant** de redémarrer ? Un serveur qui ne
remonte pas se découvre au pire moment, et l'outil que tout le monde cite ne
voit pas tout.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/

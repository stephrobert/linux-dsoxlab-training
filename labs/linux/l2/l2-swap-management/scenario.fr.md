# Contexte — Ajouter du swap à un serveur juste en mémoire

Vous administrez **alma-rhcsa-1.lab**. Un traitement par lots fait
ponctuellement grimper la mémoire, et le OOM killer du noyau l'a déjà tué
deux fois. En attendant la correction du traitement, il vous faut une
**soupape** : un petit espace de swap qui absorbe les pics, sans pour autant
faire swapper la machine en permanence.

Votre mission :

1. Ajouter un **swap file de 256 Mo**, sécurisé (`0600`) et actif.
2. Le rendre **persistant au redémarrage** via `/etc/fstab`.
3. Régler **`vm.swappiness = 10`** pour n'utiliser le swap qu'en dernier recours.

La méthode complète est dans le guide associé :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/

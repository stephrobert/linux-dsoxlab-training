# Contexte — Ajouter du swap à un serveur juste en mémoire

Vous administrez **alma-rhcsa-1.lab**. Un traitement par lots fait
ponctuellement grimper la mémoire, et le OOM killer du noyau l'a déjà tué
deux fois. En attendant la correction du traitement, il vous faut une
**soupape** : un petit espace de swap qui absorbe les pics, sans pour autant
faire swapper la machine en permanence.

Deux exigences vont de pair : cette soupape doit être là au prochain démarrage,
et le noyau ne doit y recourir qu'en dernier ressort.

La méthode complète est dans le guide associé :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/

# Contexte — laisser passer le service web à travers le pare-feu

Un serveur web va tourner sur cette machine, mais `firewalld` bloque HTTP. Ouvre
le service `http` — et fais en sorte que ça tienne après un reload et un reboot,
pas seulement jusqu'au prochain `firewall-cmd --reload`.

Ta mission, sur la VM :

1. Ajoute le service `http` à `firewalld`, de façon **permanente**
   (`firewall-cmd --permanent --add-service=http`).
2. Applique maintenant (`firewall-cmd --reload`).
3. **Ne ferme jamais `ssh`** — c'est ton accès.

L'idée : `firewall-cmd --add-service=http` (runtime) est perdu au reload/reboot ;
`--permanent` l'écrit dans la config de zone, et `--reload` relit le permanent
dans le runtime. Il faut que **les deux** listes, runtime et permanent, montrent
`http`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/

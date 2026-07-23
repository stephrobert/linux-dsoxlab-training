# Contexte — laisser passer le service web à travers le pare-feu

Un serveur web va tourner sur cette machine, mais `firewalld` bloque HTTP. Ouvre
le service `http`, et fais en sorte que ça tienne après un reload et après un
reboot, pas seulement jusqu'au prochain rechargement du pare-feu.

L'idée : un pare-feu a deux états, celui qui tourne et celui qui est écrit sur
disque. Une règle posée à chaud est perdue au premier reload comme au reboot. À
l'arrivée, **les deux** listes, runtime et permanent, doivent montrer `http`.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/

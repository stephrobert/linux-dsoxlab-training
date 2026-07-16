# Contexte — un conteneur qui revient après reboot

Un conteneur lancé avec `podman run` meurt avec la machine et ne revient jamais.
Sur RHEL, la façon moderne d'en faire un service à part entière, persistant au
boot, c'est **Quadlet** : une unité `.container` que systemd transforme en vrai
service.

Ta mission, sur la VM :

1. Écris `/etc/containers/systemd/weblab.container` décrivant un conteneur nommé
   `weblab` à partir de `registry.access.redhat.com/ubi9/ubi-micro`, exécutant
   `sleep infinity`, avec une section `[Install]` pour qu'il démarre au boot.
2. `systemctl daemon-reload` (Quadlet génère `weblab.service`).
3. Démarre-le : `systemctl start weblab.service`.

L'idée : Quadlet lit `/etc/containers/systemd/*.container` et génère des services
systemd au `daemon-reload` ; c'est le `[Install] WantedBy=` qui le câble pour
démarrer au boot. C'est ce que veut dire aujourd'hui l'objectif RHCSA « démarrer
un conteneur au boot » — pas un `podman run` bricolé dans rc.local.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/

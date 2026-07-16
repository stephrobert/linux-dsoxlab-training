# Contexte — le réseau statique façon Ubuntu : netplan

Debian/Ubuntu décrivent le réseau dans des fichiers YAML **netplan** sous
`/etc/netplan/` ; `netplan apply` les rend vers le backend (systemd-networkd ou
NetworkManager) et les active — et ça persiste au reboot. Tu as besoin d'une
adresse fixe et d'une route statique sur une interface dédiée.

Ta mission, sur la VM Ubuntu (utilise l'interface dédiée `lab0`, **ne touche jamais
à l'interface de gestion** — celle qui porte ta route par défaut) :

1. Crée **`/etc/netplan/99-lab.yaml`** (mode `0600`) qui déclare, sur une interface
   `dummy-devices` **`lab0`** :
   - l'adresse statique **`192.0.2.50/24`** ;
   - une **route** statique vers **`198.51.100.0/24` via `192.0.2.1`**.
2. **Applique** : `sudo netplan apply` (vérifie d'abord avec
   `sudo netplan generate`).

L'idée : netplan est déclaratif — tu édites du YAML, pas des commandes `ip`, et
`netplan apply` rend le tout actif et persistant. `netplan generate` valide la
syntaxe avant d'appliquer. `ip addr` / `ip route` montrent le résultat.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/

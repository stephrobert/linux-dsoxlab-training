# Une adresse statique qui survit au reboot

## La situation

Un service a besoin d'une IPv4 fixe sur cette machine, sur une interface dédiée,
et elle doit revenir après un reboot, pas disparaître. Un `ip addr add` ne dure
que jusqu'au prochain redémarrage ; la façon durable sur RHEL est un **profil de
connexion NetworkManager**.

Tu travailles sur l'interface dédiée `lab0`. **Ne touche jamais à l'interface de
gestion**, celle qui porte ta route par défaut : c'est ton lien vers la machine.

L'idée : un profil de connexion NetworkManager est écrit sur disque, et c'est ce
fichier qui fait revenir l'adresse après un reboot. Encore faut-il que le profil
soit non seulement créé, mais aussi actif : les deux se vérifient séparément.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/

## Ce qui est demandé

### Mission

Donne à cette machine une IPv4 statique sur une interface dédiée, de façon
persistante.

### Objectif (état attendu)

1. Connexion NetworkManager `lab-static` sur l'interface `lab0` (type `dummy`).
2. `ipv4.method` = `manual`, `ipv4.addresses` inclut `192.0.2.50/24`.
3. Le profil est écrit sous `/etc/NetworkManager/system-connections/`
   (persistance reboot) et `lab0` porte l'adresse en live.

### Contraintes

- **Ne touche jamais à l'interface de gestion** — c'est le lien de gestion ; le modifier te
  verrouille dehors. Travaille uniquement sur `lab0`.
- On lit NetworkManager et l'interface active, pas ton historique shell.

### Validation

```bash
dsoxlab check l4-network-static-persist
```

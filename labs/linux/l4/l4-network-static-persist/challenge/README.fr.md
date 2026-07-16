# Challenge — l4-network-static-persist

## Mission

Donne à cette machine une IPv4 statique sur une interface dédiée, de façon
persistante.

## Objectif (état attendu)

1. Connexion NetworkManager `lab-static` sur l'interface `lab0` (type `dummy`).
2. `ipv4.method` = `manual`, `ipv4.addresses` inclut `192.0.2.50/24`.
3. Le profil est écrit sous `/etc/NetworkManager/system-connections/`
   (persistance reboot) et `lab0` porte l'adresse en live.

## Contraintes

- **Ne touche jamais à `enp5s0`** — c'est le lien de gestion ; le modifier te
  verrouille dehors. Travaille uniquement sur `lab0`.
- On lit NetworkManager et l'interface active, pas ton historique shell.

## Validation

```bash
dsoxlab check l4-network-static-persist
```

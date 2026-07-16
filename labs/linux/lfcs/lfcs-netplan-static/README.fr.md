# Lab — IP statique & route avec netplan

> Préparer : `dsoxlab provision` puis `dsoxlab run lfcs-netplan-static`

## Rappel

[**netplan sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/)

netplan décrit le réseau dans `/etc/netplan/*.yaml`. Un device reçoit
`addresses:` pour les IP statiques et `routes:` (`to:`/`via:`) pour les routes
statiques. `netplan generate` valide, `netplan apply` rend et active (persistant
au boot). Les fichiers de config doivent être en `0600`.

Travaille sur `lab0`, jamais sur `enp5s0` (gestion).

## Objectifs

- `/etc/netplan/99-lab.yaml` déclare `lab0` avec `192.0.2.50/24` et la route ;
- `lab0` porte `192.0.2.50` en live ;
- la route vers `198.51.100.0/24` est présente.

## Valider

```bash
dsoxlab check lfcs-netplan-static
```

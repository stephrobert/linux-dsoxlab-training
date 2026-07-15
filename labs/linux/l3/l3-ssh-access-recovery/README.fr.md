# Lab — récupérer une config sshd cassée

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-ssh-access-recovery`

## Rappel

[**Perte d'accès SSH sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/)

sshd lit `/etc/ssh/sshd_config` et les drop-ins de `/etc/ssh/sshd_config.d/`.
`sshd -t` valide la config hors ligne — une config cassée ne mord qu'au prochain
reload/reboot, donc lance **toujours** `sshd -t` avant de recharger. `sshd -T`
affiche les réglages effectifs. `systemctl reload sshd` applique une config
valide sans couper les connexions.

## Objectifs

- `sshd -t` réussit (directive invalide corrigée) ;
- sshd tourne ;
- `PermitRootLogin no` effectif (`sshd -T`).

## Valider

```bash
dsoxlab check l3-ssh-access-recovery
```

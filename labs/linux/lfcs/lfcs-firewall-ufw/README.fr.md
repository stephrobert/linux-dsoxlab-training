# Lab — pare-feu Debian avec ufw

> Préparer : `dsoxlab provision` puis `dsoxlab run lfcs-firewall-ufw`

## Rappel

[**ufw sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/)

`ufw allow <service|port>` ajoute une règle ; `ufw enable` active le pare-feu et le
rend persistant au boot ; `ufw status` montre les règles. C'est le pendant Debian
de `firewall-cmd`. Garde toujours `OpenSSH` autorisé avant d'activer.

## Objectifs

- ufw est `active` ;
- `http` (80/tcp) est autorisé ;
- `OpenSSH` est toujours autorisé.

## Valider

```bash
dsoxlab check lfcs-firewall-ufw
```

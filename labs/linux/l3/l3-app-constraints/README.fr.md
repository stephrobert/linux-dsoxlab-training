# Lab — limites de ressources par utilisateur

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-app-constraints`

## Rappel

[**Limites de ressources sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/)

`ulimit -n` montre la limite de fichiers ouverts d'un shell ; la politique
durable est dans `/etc/security/limits.conf` et `/etc/security/limits.d/*.conf`,
une règle par ligne `<domaine> <type> <item> <valeur>` (ex.
`appuser hard nofile 8192`). `pam_limits` les applique au login. La limite
**souple** est le défaut, la **dure** est le plafond.

## Objectifs

Pour `appuser` :

- `nofile` souple = 4096, dure = 8192 (dans `limits.d/`) ;
- effectif dans une session (`su - appuser -c 'ulimit -Sn'`).

## Valider

```bash
dsoxlab check l3-app-constraints
```

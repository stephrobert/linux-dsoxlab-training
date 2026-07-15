# Lab — créer un service systemd

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-service-create-unit`

## Rappel

[**Services systemd sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/)

Une unit `.service` dans `/etc/systemd/system/` a des sections `[Unit]`,
`[Service]` (`Type=`, `ExecStart=`, `Restart=`) et `[Install]` (`WantedBy=`).
Après l'avoir écrite ou modifiée, lance `systemctl daemon-reload`. `enable` la
relie à une cible (persistance au boot) ; `start` la lance maintenant ;
`enable --now` fait les deux.

## Objectifs

- `/etc/systemd/system/labapp.service` lance `/usr/local/bin/labapp.sh` ;
- service **actif** et **activé** ;
- il tourne vraiment (`/run/labapp.status` = `running`).

## Valider

```bash
dsoxlab check l3-service-create-unit
```

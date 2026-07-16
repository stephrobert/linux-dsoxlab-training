# Lab — booléen SELinux et étiquetage de port

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-selinux-boolean-port`

## Rappel

[**SELinux sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Sous SELinux enforcing, on accorde l'accès sans le désactiver. Les **booléens**
basculent des interrupteurs de policy prédéfinis — `setsebool -P <bool> on` les
rend persistants. L'**étiquetage de port** permet à un service confiné d'ouvrir un
port non standard — `semanage port -a -t <type> -p tcp <port>`. Lecture avec
`getsebool` et `semanage port -l`.

## Objectifs

- `httpd_can_network_connect` est `on` et persistant ;
- `8404/tcp` est étiqueté `http_port_t`.

## Valider

```bash
dsoxlab check l4-selinux-boolean-port
```

# Lab — synchroniser l'horloge avec chrony

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-ntp-sync`

## Rappel

[**La synchronisation du temps avec chrony sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/reseau/chrony/)

`chronyd` est le client NTP sur les systèmes de la famille RHEL. `timedatectl`
affiche et règle le fuseau (`set-timezone`) et active le temps réseau
(`set-ntp`). Un service doit être `enabled` pour revenir après un reboot — qu'il
tourne ne suffit pas.

## Objectifs

- le fuseau est `Europe/Paris` ;
- le NTP est activé (`timedatectl show -p NTP` → `yes`) ;
- `chronyd` tourne **et** est activé.

## Valider

```bash
dsoxlab check l4-ntp-sync
```

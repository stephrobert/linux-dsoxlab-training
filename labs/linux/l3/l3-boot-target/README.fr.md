# Lab — cible de démarrage par défaut

> Prépare : `dsoxlab provision` puis `dsoxlab run l3-boot-target`

## Rappel

[**Démarrage et reboot sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/)

systemd démarre dans une **cible** (target). `systemctl get-default` montre le
défaut ; `systemctl set-default <cible>` le change (un lien symbolique,
persistant). `multi-user.target` est l'état serveur standard sans graphique ;
`systemctl isolate <cible>` bascule à chaud sans reboot.

## Objectifs

- cible par défaut = `multi-user.target` (`systemctl set-default`).

## Valider

```bash
dsoxlab check l3-boot-target
```

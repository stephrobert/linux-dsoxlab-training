# Lab — gérer un profil AppArmor

> Préparer : `dsoxlab provision` puis `dsoxlab run lfcs-apparmor`

## Rappel

[**AppArmor sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/)

AppArmor confine les programmes avec des profils par binaire. `aa-status` liste les
profils chargés et leur mode ; `aa-complain <profil>` passe un profil en mode
apprentissage (journalise, ne bloque pas), `aa-enforce` le remet en enforce,
`aa-disable` le décharge. C'est le pendant Debian de SELinux, mais par profil.

## Objectifs

- AppArmor est actif avec des profils chargés ;
- le profil `ping` est en mode `complain` (`aa-status`).

## Valider

```bash
dsoxlab check lfcs-apparmor
```

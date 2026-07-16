# Lab — paramètre noyau persistant au démarrage

> Préparer : `dsoxlab provision` puis `dsoxlab run l3-grub-kernel-args`

## Rappel

[**GRUB sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/durcissement/grub/)

`grubby --update-kernel=ALL --args="param"` ajoute un argument noyau aux noyaux
installés ; `--remove-args` le retire ; `--info=DEFAULT` montre les arguments du
noyau par défaut. Pour les **futurs** noyaux, ajoute le paramètre à
`GRUB_CMDLINE_LINUX` dans `/etc/default/grub` (le modèle de `grub2-mkconfig`). Les
deux sont nécessaires pour une vraie persistance.

## Objectifs

- les arguments du noyau par défaut incluent `panic=10` (`grubby --info=DEFAULT`) ;
- `/etc/default/grub` contient `panic=10`.

## Valider

```bash
dsoxlab check l3-grub-kernel-args
```

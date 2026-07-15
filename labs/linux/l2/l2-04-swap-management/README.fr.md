# Lab — Ajouter et gérer le swap

> Chaque lab est autonome. Prérequis : la VM du lab doit tourner et être
> joignable en SSH+sudo. Préparez-la avec :
>
> ```bash
> dsoxlab run l2-04-swap-management
> ```

## Rappel

[**Gérer le swap sous Linux**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/)

Le swap est un espace disque que le noyau utilise comme extension de la RAM :
quand la mémoire se remplit, les pages inactives y sont déplacées. Il absorbe
les pics et permet l'hibernation, mais un système qui swappe en permanence est
lent. Le swap file est l'option la plus souple ; il doit être en `0600` car il
contient des pages mémoire.

## Objectifs

À la fin de ce lab, vous saurez :

- Créer un **swap file sécurisé** (`0600`) et l'activer (`mkswap`, `swapon`).
- Rendre le swap **persistant** au démarrage via `/etc/fstab`.
- Régler **`vm.swappiness`** durablement avec un fichier `/etc/sysctl.d/`.

## Lancer et valider

```bash
dsoxlab run   l2-04-swap-management    # prépare la VM
dsoxlab check l2-04-swap-management    # note votre travail
```

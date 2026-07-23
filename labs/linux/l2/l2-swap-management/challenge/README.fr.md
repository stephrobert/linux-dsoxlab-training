# Challenge — l2-04 : Ajouter et gérer de l'espace de swap

## Mission

Sur **alma-rhcsa-1.lab**, ajoute un **fichier de swap de 256 MiB** au système,
rends-le sûr et persistant, et règle le comportement du noyau vis-à-vis du swap.

Tu dois :

1. Créer un fichier de swap `/swapfile` de **256 MiB**, appartenant à `root:root`, en mode **0600**.
2. Le formater (`mkswap`) et l'**activer** (`swapon`).
3. Le rendre **persistant** au redémarrage via `/etc/fstab`.
4. Fixer durablement **`vm.swappiness = 10`** (drop-in dans `/etc/sysctl.d/`).

## Contraintes

- Le fichier de swap **doit** être en mode `0600` (il contient des pages mémoire).
- L'entrée fstab doit référencer `/swapfile` avec le type `swap`.
- `vm.swappiness` doit valoir `10` (`sysctl -n vm.swappiness`).

## Approche utile

Les gestes se déduisent du guide compagnon, dont le lien figure dans le
`## Rappel` du cours. Si tu bloques, `dsoxlab hint` les donne, au prix
annoncé.

## Validation

```bash
dsoxlab check l2-swap-management
```

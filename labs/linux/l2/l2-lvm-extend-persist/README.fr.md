# Lab — Étendre un volume logique, durablement

> Prépare la VM : `dsoxlab run l2-lvm-extend-persist`

## Rappel

[**LVM sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/)

Un volume logique peut grandir alors qu'il est monté. L'ordre compte : d'abord
`lvextend` sur le volume logique, ensuite l'agrandissement du **filesystem** par
dessus (`xfs_growfs` pour XFS, `resize2fs` pour ext4). Étendre le LV sans
agrandir le filesystem est l'erreur la plus courante : l'espace ajouté reste
invisible. La persistance vit dans `/etc/fstab`, toujours par **UUID**.

## Objectifs

- Étendre le volume logique `vgdata/lvdata` à au moins **3 GiB**.
- Agrandir le filesystem **XFS** pour que `/data` reflète vraiment la taille.
- Garder le montage persistant au reboot (fstab par UUID).

## Lancer et valider

```bash
dsoxlab run l2-lvm-extend-persist
# … résous sur la VM …
dsoxlab check l2-lvm-extend-persist
```

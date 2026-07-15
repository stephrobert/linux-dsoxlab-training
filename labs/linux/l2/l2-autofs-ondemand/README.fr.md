# Lab — montages à la demande avec autofs

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-autofs-ondemand`

## Rappel

[**autofs sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/)

autofs monte un chemin seulement à l'accès et le démonte après un `--timeout`
d'inactivité. Une **carte maître** (`/etc/auto.master` ou un fichier de
`/etc/auto.master.d/`) associe un point de montage à une **carte de montage** ;
la carte de montage liste des clés et comment les monter :
`clé  -fstype=xfs  :/dev/sdX1`. `systemctl restart autofs` recharge les cartes.

## Objectifs

- carte maître : `/autofs` → `/etc/auto.lab` ;
- carte de montage `/etc/auto.lab` : `data -fstype=xfs :<partition>` ;
- autofs activé et démarré ;
- accéder à `/autofs/data` le monte (marker.txt lisible).

## Valider

```bash
dsoxlab check l2-autofs-ondemand
```

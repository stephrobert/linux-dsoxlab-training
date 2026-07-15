# Lab — Chiffrer un disque avec LUKS

> Préparez la VM : `dsoxlab run l2-luks-encryption`

## Rappel

[**Le chiffrement de disque avec LUKS**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/)

LUKS chiffre un périphérique bloc : sans la clé, les données sont illisibles.
L'ordre est toujours format -> open -> mkfs sur le mapping -> mount. La
persistance se déclare dans `/etc/crypttab` (qui crée `/dev/mapper/...`) plus
`/etc/fstab`.

## Objectifs

- Formater un disque en **LUKS2** et l'ouvrir.
- Poser un système de fichiers sur le mapping et le monter.
- Le faire déverrouiller au boot via **`/etc/crypttab`**.

## Lancer et valider

```bash
dsoxlab run   l2-luks-encryption
dsoxlab check l2-luks-encryption
```

# Lab — déléguer un sudo limité

> Prépare : `dsoxlab provision` puis `dsoxlab run l2-sudo-delegation`

## Rappel

[**sudo sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/)

Mets la politique sudo dans des drop-ins `/etc/sudoers.d/` (mode `0440`). Une
règle se lit `qui où=(en-tant-que) commandes` ; `%groupe` cible un groupe,
`NOPASSWD:` supprime la demande de mot de passe, et lister des commandes
explicites, c'est le moindre privilège. **Toujours** valider avec
`visudo -cf <fichier>` — une erreur de syntaxe peut casser tout sudo.
`sudo -l -U <user>` montre la politique effective.

## Objectifs

- drop-in `/etc/sudoers.d/operators` ;
- `%operators` peut lancer **seulement** `/usr/bin/systemctl`, `NOPASSWD` ;
- sudoers reste valide (`visudo -c`).

## Valider

```bash
dsoxlab check l2-sudo-delegation
```

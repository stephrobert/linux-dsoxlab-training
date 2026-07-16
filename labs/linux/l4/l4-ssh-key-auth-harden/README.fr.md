# Lab — accès SSH par clé durci pour un utilisateur de service

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-ssh-key-auth-harden`

## Rappel

[**Les clés SSH sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/)

`sshd` impose des permissions strictes sur les fichiers de clés : `~/.ssh` doit
être `0700` et détenu par l'utilisateur, `authorized_keys` doit être `0600` et
détenu par l'utilisateur. Trop ouvert, ou détenu par un autre, et la clé est
**ignorée en silence**. Lis-les avec `stat -c '%a %U:%G'`.

## Objectifs

- l'utilisateur `deploy` existe ;
- `~deploy/.ssh` est `0700`, détenu `deploy:deploy` ;
- `~deploy/.ssh/authorized_keys` est `0600`, détenu `deploy:deploy`, clé présente.

## Valider

```bash
dsoxlab check l4-ssh-key-auth-harden
```

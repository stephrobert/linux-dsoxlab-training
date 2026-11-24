# Une auth par clé qui refuse en silence

## La situation

Un utilisateur de service `deploy` doit se connecter en SSH avec sa clé, et la
clé publique est déjà dans `~deploy/.ssh/authorized_keys`. Pourtant `sshd` la
refuse et retombe sur rien. La clé est bonne ; ce sont les **permissions** qui ne
le sont pas : `sshd` ignore un `authorized_keys` accessible en écriture au groupe
ou aux autres, ou non détenu par l'utilisateur.

L'idée : l'auth SSH par clé, c'est autant une affaire de **propriétaire et de
permissions** que de clé. `sshd` refuse silencieusement un `authorized_keys` dont
l'environnement est trop ouvert ou mal détenu, sans rien annoncer côté client :
c'est le piège qui fait perdre des heures.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/

## Ce qui est demandé

### Mission

`deploy` a sa clé dans `authorized_keys` mais `sshd` la refuse — corrige le
propriétaire et les permissions.

### Objectif (état attendu)

1. L'utilisateur `deploy` existe.
2. `~deploy/.ssh` → répertoire, `0700`, détenu `deploy:deploy`.
3. `~deploy/.ssh/authorized_keys` → `0600`, détenu `deploy:deploy`, clé conservée.

### Contraintes

- Ne change pas le contenu de la clé — seuls le propriétaire et les permissions
  sont faux.
- On lit l'état du système de fichiers (`stat`), pas ton historique.

### Validation

```bash
dsoxlab check l4-ssh-key-auth-harden
```

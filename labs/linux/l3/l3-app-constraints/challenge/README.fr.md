# Relever le plafond de ressources d'une application

## La situation

Le service qui tourne sous **`appuser`** ouvre des milliers de fichiers et bute
sur la limite par défaut de fichiers ouverts. Tu dois relever sa limite `nofile`
— et la rendre durable pour chaque nouvelle session, pas juste ce shell.

L'idée : ce qu'on ajuste dans un shell ne vaut que pour ce shell. Une politique
durable se déclare ailleurs et s'applique à l'ouverture de chaque session. Et
deux valeurs cohabitent : la limite souple, qui est le défaut appliqué, et la
limite dure, qui est le plafond que l'utilisateur peut atteindre.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/

## Ce qui est demandé

### Mission

Relève la limite de fichiers ouverts d'`appuser`, durablement.

### Objectif (état attendu)

1. Un drop-in `/etc/security/limits.d/` définit `nofile` pour appuser.
2. Effectif : `su - appuser -c 'ulimit -Sn'` → **4096** (souple).
3. Effectif : `su - appuser -c 'ulimit -Hn'` → **8192** (dure).

### Contraintes

- Édite `/etc/security/limits.d/appuser.conf`. La validation lit la limite
  **effective** dans une session de login (via pam_limits), pas la commande.

### Validation

```bash
dsoxlab check l3-app-constraints
```

# Transformer un programme en service géré

## La situation

Un petit programme (`/usr/local/bin/labapp.sh`) doit tourner comme un vrai
**service systemd** : démarré maintenant, redémarré en cas d'échec, et relancé
automatiquement au boot. Là, il n'a aucune unit.

L'idée : un fichier unit décrit *comment* lancer quelque chose. Reste à savoir
comment faire prendre en compte cette description par systemd, puis à distinguer
« tourne maintenant » de « revient au prochain boot » : ce sont deux gestes
distincts.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/

## Ce qui est demandé

### Mission

Transforme `/usr/local/bin/labapp.sh` en service systemd géré.

### Objectif (état attendu)

1. Une unit `/etc/systemd/system/labapp.service` avec `ExecStart=/usr/local/bin/labapp.sh`.
2. Service **actif** (`is-active`).
3. Service **activé** au boot (`is-enabled`).
4. Il a réellement tourné (`/run/labapp.status` = `running`).

### Contraintes

- `daemon-reload` après écriture de l'unit, puis `systemctl enable --now labapp`.
  La validation lit l'**état réel** du service (pas la commande).

### Validation

```bash
dsoxlab check l3-service-create-unit
```

# Challenge — l3-service-create-unit

## Mission

Transforme `/usr/local/bin/labapp.sh` en service systemd géré.

## Objectif (état attendu)

1. Une unit `/etc/systemd/system/labapp.service` avec `ExecStart=/usr/local/bin/labapp.sh`.
2. Service **actif** (`is-active`).
3. Service **activé** au boot (`is-enabled`).
4. Il a réellement tourné (`/run/labapp.status` = `running`).

## Contraintes

- `daemon-reload` après écriture de l'unit, puis `systemctl enable --now labapp`.
  La validation lit l'**état réel** du service (pas la commande).

## Validation

```bash
dsoxlab check l3-service-create-unit
```

# Challenge — l2-disk-space-troubleshoot

## Mission

`/srv/data` est presque plein sur la VM. Diagnostique et récupère de l'espace.

## Objectif (état attendu)

1. `/srv/data` est **toujours monté**.
2. Son occupation est **sous 50 %**.
3. Le fichier légitime `/srv/data/app.log` est **conservé**.

## Contraintes

- Diagnostique avec `df -h` puis `du -h --max-depth=1 /srv/data`. Ne supprime que
  le superflu (le cache), pas les données légitimes ; ne démonte/reformate pas.
- La validation lit l'**état réel** (montage, occupation `df`, présence app.log).

## Validation

```bash
dsoxlab check l2-disk-space-troubleshoot
```

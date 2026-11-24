# Le disque est plein

## La situation

Une alerte tombe : les écritures dans `/srv/data` échouent, « No space left on
device ». Un filesystem y est presque plein. Ta mission, c'est le réflexe ops du
quotidien : trouver ce qui mange l'espace et le récupérer — **sans** effacer les
données qui comptent.

L'idée : mesurer l'occupation d'un filesystem et attribuer cette occupation aux
répertoires qui la causent, ce sont deux gestes différents. Un piège classique
(RHCSA) : quand les deux mesures se contredisent, c'est qu'un processus tient
encore un fichier supprimé mais toujours ouvert, et l'espace ne revient que
lorsqu'il le relâche. Ici, rassure-toi, le coupable est bien un fichier présent
sur le disque.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/

## Ce qui est demandé

### Mission

`/srv/data` est presque plein sur la VM. Diagnostique et récupère de l'espace.

### Objectif (état attendu)

1. `/srv/data` est **toujours monté**.
2. Son occupation est **sous 50 %**.
3. Le fichier légitime `/srv/data/app.log` est **conservé**.

### Contraintes

- Diagnostique avec `df -h` puis `du -h --max-depth=1 /srv/data`. Ne supprime que
  le superflu (le cache), pas les données légitimes ; ne démonte/reformate pas.
- La validation lit l'**état réel** (montage, occupation `df`, présence app.log).

### Validation

```bash
dsoxlab check l2-disk-space-troubleshoot
```

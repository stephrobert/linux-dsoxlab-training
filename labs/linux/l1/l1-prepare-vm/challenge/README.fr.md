# Challenge — l1-03 : Inventorier les ressources de ta machine

Travaille dans **`challenge/work/`** — le fichier `vm-info.txt` y a été créé par
`dsoxlab run`.

---

## Mission

Devant une machine neuve, le premier réflexe d'un administrateur est de savoir
**de quoi elle dispose**. Inventorie les ressources de ta machine et relève
quatre valeurs réelles dans `vm-info.txt` :

1. `CPU_COUNT` — le nombre de processeurs, via `nproc`.
2. `ARCH` — l'architecture, via `uname -m`.
3. `MEM_TOTAL_KB` — la mémoire totale en kB, dans `/proc/meminfo`.
4. `BLOCK_DEVICE` — le nom d'**un** disque réel, via `lsblk`.

## Contraintes

- Chaque valeur doit être la **vraie valeur de ta machine** : la validation la
  compare à l'état réel du système. Une valeur inventée échoue.
- Tous les placeholders `VOTRE_RÉPONSE_ICI` doivent être remplacés.

## Commandes utiles

```bash
nproc
uname -m
grep MemTotal /proc/meminfo
lsblk -dno NAME
```

## Validation

```bash
dsoxlab check l1-prepare-vm
```

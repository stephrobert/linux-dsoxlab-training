# Challenge — l1-01 : Cartographier ton système Linux

Travaille dans **`challenge/work/`** — le fichier `notions.md` y a été créé par
`dsoxlab run`. Complète-le sans pas-à-pas.

---

## Mission

Tu prépares ton premier poste Linux. Avant de toucher à quoi que ce soit, tu dois
savoir sur quoi tu travailles. **Explore ta machine** et relève quatre faits
réels dans `notions.md` :

1. `KERNEL` — la version de ton noyau, via `uname -r`.
2. `DISTRO_ID` — l'identifiant de ta distribution, dans `/etc/os-release`.
3. `ETC_FILE` — le nom d'**un** fichier réellement présent dans `/etc`.
4. `LOG_FILE` — le nom d'**un** fichier réellement présent dans `/var/log`.

## Contraintes

- Chaque champ doit contenir la **vraie valeur de ta machine**, pas un exemple.
  La validation compare tes réponses à l'état réel du système : une valeur
  inventée échoue.
- Tous les placeholders `VOTRE_RÉPONSE_ICI` doivent être remplacés.

## Commandes utiles

```bash
uname -r
grep '^ID=' /etc/os-release
ls /etc
ls /var/log
```

## Validation

```bash
dsoxlab check l1-01-discover-linux-map   # valide ton travail
dsoxlab hint  l1-01-discover-linux-map   # bloqué ? un indice (coûte des points)
```

> Les **concepts** (à quoi sert un noyau, en quoi une distribution diffère du
> noyau, le rôle de `/etc` et `/var/log`) sont traités dans le cours et vérifiés
> par le quiz associé. Ce lab, lui, prouve que tu as réellement exploré ton
> système.

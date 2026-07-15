# Challenge — l1-02 : Reconnaître l'écosystème de ta distribution

Travaille dans **`challenge/work/`** — le fichier `choix-distro.txt` y a été créé
par `dsoxlab run`.

---

## Mission

Chaque famille de distributions a son écosystème : famille, gestionnaire de
paquets, commandes. Avant d'installer quoi que ce soit, tu dois savoir
**laquelle tu utilises**. Identifie l'écosystème réel de ta machine et relève
trois valeurs dans `choix-distro.txt` :

1. `FAMILY` — la famille de ta distribution (`debian`, `rhel`, `suse`, `arch`,
   `alpine`), déduite de `/etc/os-release`.
2. `PACKAGE_MANAGER` — le gestionnaire de paquets réellement présent (`apt`,
   `dnf`, `zypper`, `pacman`, `apk`).
3. `INSTALL_CMD` — la commande pour installer un paquet avec CE gestionnaire.

## Contraintes

- Chaque réponse doit correspondre à **ce que ta machine expose réellement** : la
  validation le vérifie (famille via `/etc/os-release`, gestionnaire via `which`).
  Une réponse qui ne colle pas à ta machine échoue.
- Tous les placeholders `VOTRE_RÉPONSE_ICI` doivent être remplacés.

## Commandes utiles

```bash
grep -E '^ID=|^ID_LIKE=' /etc/os-release
which apt ; which dnf ; which zypper ; which pacman ; which apk
```

## Validation

```bash
dsoxlab check l1-02-choose-distro
```

> Le **choix** d'une distribution selon un contexte (débutant, RHCSA, serveur
> perso) et les différences entre familles sont traités dans le cours et le
> quiz. Ce lab, lui, prouve que tu sais reconnaître ton propre système.

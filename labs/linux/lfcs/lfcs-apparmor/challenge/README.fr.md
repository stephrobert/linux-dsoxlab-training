# Challenge — lfcs-apparmor

## Mission

Passe le profil AppArmor `ping` en mode complain.

## Objectif (état attendu)

1. AppArmor est actif avec des profils chargés.
2. Le profil `ping` est en mode `complain` (`aa-status`).

## Contraintes

- Utilise l'outillage AppArmor (`aa-complain`), pas SELinux.
- Ne désactive pas AppArmor globalement — bascule ce seul profil.
- On lit `aa-status --json`.

## Validation

```bash
dsoxlab check lfcs-apparmor
```

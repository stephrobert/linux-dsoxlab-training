# Le pare-feu Debian : ufw

## La situation

Sur Debian et Ubuntu, la façade conviviale du pare-feu est **`ufw`**
(Uncomplicated FireWall). Un service web doit être joignable, tu vas donc ouvrir
`http` et activer le pare-feu, tout en gardant ton accès SSH.

L'idée : `ufw` est le pendant Debian de `firewall-cmd`, même principe, syntaxe
volontairement minimale. Le pare-feu a un état actif ou inactif qui lui est
propre, distinct des règles qu'il contient : les deux comptent, et l'ordre dans
lequel tu t'en occupes décide si tu gardes ta session ouverte ou non.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/reseaux/ufw/

## Ce qui est demandé

### Mission

Ouvre `http` et active ufw, en gardant SSH joignable.

### Objectif (état attendu)

1. ufw est `active` (`ufw status`).
2. `http` / `80/tcp` est autorisé.
3. `OpenSSH` est toujours autorisé.

### Contraintes

- **Ne retire jamais `OpenSSH`** — c'est ton accès ; il est déjà autorisé.
- Utilise `ufw` (Debian), pas `firewall-cmd`.
- On lit `ufw status`.

### Validation

```bash
dsoxlab check lfcs-firewall-ufw
```

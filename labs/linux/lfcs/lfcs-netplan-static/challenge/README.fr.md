# Le réseau statique façon Ubuntu : netplan

## La situation

Debian et Ubuntu décrivent le réseau dans des fichiers YAML **netplan** sous
`/etc/netplan/`. Tu as besoin d'une adresse fixe et d'une route statique sur une
interface dédiée, et il faut que les deux reviennent après un reboot.

Tu travailles sur l'interface dédiée `lab0`. **Ne touche jamais à l'interface de
gestion**, celle qui porte ta route par défaut : c'est ton lien vers la machine.

L'idée : netplan est déclaratif, on décrit l'état voulu en YAML au lieu
d'enchaîner des commandes `ip`. Écrire le fichier ne suffit pas : tant qu'il n'a
pas été rendu vers le backend réseau, rien ne change sur la machine. Et se
tromper de contenu sur une machine distante, c'est perdre la main dessus.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/

## Ce qui est demandé

### Mission

Configure une IP statique et une route statique avec netplan sur une interface
dédiée.

### Objectif (état attendu)

1. `/etc/netplan/99-lab.yaml` déclare `lab0` (dummy) avec `192.0.2.50/24` et une
   route vers `198.51.100.0/24 via 192.0.2.1`.
2. `lab0` porte `192.0.2.50` en live.
3. La route vers `198.51.100.0/24` est présente.

### Contraintes

- **Ne touche jamais à l'interface de gestion** — celle qui porte ta route par défaut. Travaille sur `lab0`.
- Fichier de config `0600` ; applique avec `netplan apply`.
- On lit le fichier netplan, `ip addr` et `ip route`.

### Validation

```bash
dsoxlab check lfcs-netplan-static
```

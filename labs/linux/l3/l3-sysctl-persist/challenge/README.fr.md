# Durcir le noyau, définitivement

## La situation

Un scan de sécurité épingle cet hôte : il route des paquets IP et accepte les
redirections ICMP, alors qu'aucun des deux n'est souhaité sur un serveur normal.
Désactive-les, au niveau du noyau, pour que ça tienne maintenant **et** après un
reboot.

L'idée : un paramètre `sysctl` se change à chaud, mais ce qui est posé à chaud
disparaît au redémarrage. Rendre le réglage actif tout de suite et le rendre
durable sont deux gestes distincts : les tests regarderont les deux.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/durcissement/sysctl/

## Ce qui est demandé

### Mission

Durcis le noyau : coupe le routage IP et les redirections ICMP, durablement.

### Objectif (état attendu)

1. `sysctl -n net.ipv4.ip_forward` → **0** (live).
2. `sysctl -n net.ipv4.conf.all.accept_redirects` → **0** (live).
3. Les deux sont déclarés dans `/etc/sysctl.d/` (persistance reboot).

### Contraintes

- Drop-in `/etc/sysctl.d/99-hardening.conf`, puis `sudo sysctl --system`. La
  validation lit les **valeurs actives** du noyau + le contenu de sysctl.d.

### Validation

```bash
dsoxlab check l3-sysctl-persist
```

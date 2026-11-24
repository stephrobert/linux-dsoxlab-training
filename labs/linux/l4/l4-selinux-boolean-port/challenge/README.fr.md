# SELinux est enforcing, et il dit non

## La situation

SELinux est en mode **enforcing**. Une app web a besoin de deux choses que la
policy interdit par défaut : ouvrir des connexions réseau sortantes, et écouter
sur le port non standard **8404/tcp**. Tu ne vas pas désactiver SELinux, tu vas
accorder exactement ce qu'il faut, durablement.

L'idée : les booléens SELinux sont des interrupteurs de policy, et un
interrupteur basculé à chaud revient tout seul au reboot si on ne demande pas
explicitement le contraire. Les ports non standard, eux, doivent être
**étiquetés** : sans étiquette, un service confiné n'a tout simplement pas le
droit de s'y attacher.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/durcissement/selinux/

## Ce qui est demandé

### Mission

Sous SELinux enforcing, autorise l'app : active un booléen de façon persistante et
étiquette un port non standard.

### Objectif (état attendu)

1. `getsebool httpd_can_network_connect` → `on`, et ça survit au reboot (`-P`).
2. `8404/tcp` est étiqueté `http_port_t` (`semanage port -l`).

### Contraintes

- Ne désactive **pas** SELinux (`setenforce 0` / permissive = échec).
- On lit `getsebool` et `semanage port`, pas ton historique.

### Validation

```bash
dsoxlab check l4-selinux-boolean-port
```

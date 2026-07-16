# Challenge — l4-selinux-boolean-port

## Mission

Sous SELinux enforcing, autorise l'app : active un booléen de façon persistante et
étiquette un port non standard.

## Objectif (état attendu)

1. `getsebool httpd_can_network_connect` → `on`, et ça survit au reboot (`-P`).
2. `8404/tcp` est étiqueté `http_port_t` (`semanage port -l`).

## Contraintes

- Ne désactive **pas** SELinux (`setenforce 0` / permissive = échec).
- On lit `getsebool` et `semanage port`, pas ton historique.

## Validation

```bash
dsoxlab check l4-selinux-boolean-port
```

# Challenge — l4-reverse-proxy-lb

## Mission

Mets HAProxy devant le serveur web backend et répartis la charge vers lui.

## Objectif (état attendu)

1. `/etc/haproxy/haproxy.cfg` : un `frontend` sur `*:80` + un `backend` avec un
   `server` sur l'hôte backend port 80.
2. `haproxy` tourne et est activé.
3. `curl http://localhost/` renvoie `backend-ok` (la page du backend, à travers
   le proxy).

## Contraintes

- L'IP du backend est dans `/root/lb-backend.env`.
- Valide avec `haproxy -c` avant de démarrer.
- On lit l'état du service et une vraie requête à travers le proxy.

## Validation

```bash
dsoxlab check l4-reverse-proxy-lb
```

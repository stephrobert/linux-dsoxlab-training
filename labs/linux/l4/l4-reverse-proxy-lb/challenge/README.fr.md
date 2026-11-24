# Mettre un répartiteur de charge devant le backend

## La situation

Un backend web tourne sur un autre hôte et sert une page. Les requêtes ne doivent
pas l'atteindre directement : elles doivent passer par **HAProxy** sur cet hôte
frontal, qui fait reverse-proxy et répartit la charge vers le backend. Et ça doit
revenir après un reboot.

L'idée : HAProxy est un proxy applicatif (L7). Un `frontend` accepte les
connexions, un `backend` les transmet aux serveurs réels, et une politique de
répartition choisit lequel. À l'arrivée, une requête vers `http://localhost/` sur
cet hôte doit renvoyer la page du backend.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/services/reseau/haproxy/

## Ce qui est demandé

### Mission

Mets HAProxy devant le serveur web backend et répartis la charge vers lui.

### Objectif (état attendu)

1. `/etc/haproxy/haproxy.cfg` : un `frontend` sur `*:80` + un `backend` avec un
   `server` sur l'hôte backend port 80.
2. `haproxy` tourne et est activé.
3. `curl http://localhost/` renvoie `backend-ok` (la page du backend, à travers
   le proxy).

### Contraintes

- L'IP du backend est dans `/root/lb-backend.env`.
- Valide avec `haproxy -c` avant de démarrer.
- On lit l'état du service et une vraie requête à travers le proxy.

### Validation

```bash
dsoxlab check l4-reverse-proxy-lb
```

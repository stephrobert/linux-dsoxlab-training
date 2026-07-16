# Lab — reverse proxy & répartition de charge avec HAProxy

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-reverse-proxy-lb`

## Rappel

[**HAProxy sur le guide compagnon**](https://blog.stephane-robert.info/docs/services/reseau/haproxy/)

HAProxy est un proxy L7 : un `frontend` écoute un port, un `backend` liste les
`server`s réels et `balance` la charge entre eux. `haproxy -c -f <cfg>` valide la
conf avant de démarrer le service. L'IP de l'hôte backend est dans
`/root/lb-backend.env`.

## Objectifs

- `/etc/haproxy/haproxy.cfg` a un `frontend` sur `*:80` et un `backend` avec un
  `server` sur l'hôte backend:80 ;
- `haproxy` tourne et est activé ;
- `curl http://localhost/` renvoie la page backend (`backend-ok`).

## Valider

```bash
dsoxlab check l4-reverse-proxy-lb
```

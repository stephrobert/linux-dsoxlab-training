# Lab — reverse proxy & load balancing with HAProxy

> Prepare: `dsoxlab provision` then `dsoxlab run l4-reverse-proxy-lb`

## Recap

[**HAProxy on the companion guide**](https://blog.stephane-robert.info/docs/services/reseau/haproxy/)

HAProxy is an L7 proxy: a `frontend` binds a port, a `backend` lists real
`server`s and `balance`s across them. `haproxy -c -f <cfg>` validates the config
before you start the service. The backend host's IP is in `/root/lb-backend.env`.

## Objectives

- `/etc/haproxy/haproxy.cfg` has a `frontend` on `*:80` and a `backend` with a
  `server` on the backend host:80;
- `haproxy` is running and enabled;
- `curl http://localhost/` returns the backend page (`backend-ok`).

## Validate

```bash
dsoxlab check l4-reverse-proxy-lb
```

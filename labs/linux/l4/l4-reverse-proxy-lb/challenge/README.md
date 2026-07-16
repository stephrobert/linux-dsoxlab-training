# Challenge — l4-reverse-proxy-lb

## Mission

Put HAProxy in front of the backend web server and load-balance to it.

## Goal (expected state)

1. `/etc/haproxy/haproxy.cfg`: a `frontend` on `*:80` + a `backend` with a
   `server` on the backend host port 80.
2. `haproxy` running and enabled.
3. `curl http://localhost/` returns `backend-ok` (the backend's page, through
   the proxy).

## Constraints

- The backend IP is in `/root/lb-backend.env`.
- Validate with `haproxy -c` before starting.
- Validation reads the service state and a real request through the proxy.

## Validation

```bash
dsoxlab check l4-reverse-proxy-lb
```

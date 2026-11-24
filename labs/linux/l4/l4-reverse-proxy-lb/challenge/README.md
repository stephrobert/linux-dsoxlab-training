# Put a load balancer in front of the backend

## The situation

A web backend runs on another host and serves a page. Requests should not hit it
directly — they should go through **HAProxy** on this front host, which
reverse-proxies and load-balances to the backend. And it must come back after a
reboot.

The point: HAProxy is an application-level (L7) proxy. A `frontend` accepts
connections, a `backend` forwards them to the real servers, and a balancing
policy picks which one. In the end, a request to `http://localhost/` on this host
must return the backend's page.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/networking/haproxy/

## What is asked

### Mission

Put HAProxy in front of the backend web server and load-balance to it.

### Goal (expected state)

1. `/etc/haproxy/haproxy.cfg`: a `frontend` on `*:80` + a `backend` with a
   `server` on the backend host port 80.
2. `haproxy` running and enabled.
3. `curl http://localhost/` returns `backend-ok` (the backend's page, through
   the proxy).

### Constraints

- The backend IP is in `/root/lb-backend.env`.
- Validate with `haproxy -c` before starting.
- Validation reads the service state and a real request through the proxy.

### Validation

```bash
dsoxlab check l4-reverse-proxy-lb
```

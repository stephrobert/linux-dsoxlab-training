# Context — put a load balancer in front of the backend

A web backend runs on another host and serves a page. Requests should not hit it
directly — they should go through **HAProxy** on this front host, which
reverse-proxies and load-balances to the backend. And it must come back after a
reboot.

Your mission, on the front VM (the backend's IP is in `/root/lb-backend.env`):

1. Configure **`/etc/haproxy/haproxy.cfg`**:
   - a `frontend` that binds `*:80`;
   - a `backend` (`balance roundrobin`) with a `server` line pointing at the
     backend host on port 80.
2. **Validate** the config: `haproxy -c -f /etc/haproxy/haproxy.cfg`.
3. **Enable and start** `haproxy`.

The point: HAProxy is an application-level (L7) proxy — the `frontend` accepts
connections and the `backend` forwards them to real servers, `balance`
distributing across them. `haproxy -c` catches config errors before they take the
service down. A request to `http://localhost/` on this host must return the
backend's page.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/reseau/haproxy/

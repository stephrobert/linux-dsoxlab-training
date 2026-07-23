# Context — put a load balancer in front of the backend

A web backend runs on another host and serves a page. Requests should not hit it
directly — they should go through **HAProxy** on this front host, which
reverse-proxies and load-balances to the backend. And it must come back after a
reboot.

The point: HAProxy is an application-level (L7) proxy. A `frontend` accepts
connections, a `backend` forwards them to the real servers, and a balancing
policy picks which one. In the end, a request to `http://localhost/` on this host
must return the backend's page.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/reseau/haproxy/

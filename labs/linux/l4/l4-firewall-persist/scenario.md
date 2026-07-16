# Context — let the web service through the firewall

A web server is about to run on this host, but `firewalld` blocks HTTP. Open the
`http` service — and make it stick after a reload and a reboot, not just until
the next `firewall-cmd --reload`.

Your mission, on the VM:

1. Add the `http` service to `firewalld`, **permanently**
   (`firewall-cmd --permanent --add-service=http`).
2. Apply it now (`firewall-cmd --reload`).
3. **Never close `ssh`** — that's your way in.

The point: `firewall-cmd --add-service=http` (runtime) is lost on reload/reboot;
`--permanent` writes it to the zone config, and `--reload` re-reads permanent
into runtime. You need **both** the runtime and permanent lists to show `http`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/

# Context — let the web service through the firewall

A web server is about to run on this host, but `firewalld` blocks HTTP. Open the
`http` service — and make it stick after a reload and after a reboot, not just
until the firewall is next reloaded.

The point: a firewall has two states, the one that runs and the one written on
disk. A rule added live is lost at the first reload, and at reboot. In the end
**both** lists, runtime and permanent, must show `http`.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/

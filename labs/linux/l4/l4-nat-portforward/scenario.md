# Context — turn this host into a NAT gateway

This host must forward traffic: incoming connections on **`tcp/8080`** should be
sent to a backend server at **`192.0.2.20:80`**, with the source address
masqueraded so replies come back. And it must hold across a reboot — a NAT rule
that vanishes on restart is worse than none.

The point: forwarding traffic on someone else's behalf is not the kernel's
default behaviour, it has to be allowed. Redirecting a port and masquerading the
source address are then two distinct treatments, at two different points of a
packet's journey. And an nftables rule added live dies at reboot: persistence is
configured elsewhere.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/

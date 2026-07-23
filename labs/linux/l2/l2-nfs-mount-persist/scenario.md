# Context — mount a share from an NFS server

This lab uses **two machines**: a server (`alma-rhcsa-2`) already exports an NFS
share `/srv/export`, and your client (`alma-rhcsa-1`) must mount it. This is the
everyday "attach the shared storage" task, with its classic reboot trap: a
network mount attempted before the network is up, and the whole boot goes
sideways.

The point: a network filesystem is declared like any other, but it depends on
something the others do not need, the network. Boot does not infer that
dependency on its own: it has to be declared.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/stockage/nfs/

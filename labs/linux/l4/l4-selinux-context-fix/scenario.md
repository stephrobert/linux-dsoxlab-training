# Context — right content, wrong label

Web content was placed in a custom directory `/srv/labweb`, but under enforcing
SELinux a confined web server can't read it: the files carry the wrong type,
inherited from `/srv`. Relabel it — and make the fix **stick** through a full
relabel or a reboot, not just for the lifetime of a one-off tweak.

The point: a label set by hand on a file is wiped by the system's next relabel.
The durable way, the one RHCSA expects, is to **declare the rule** that says
which type this path must carry, then let the policy apply it.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/

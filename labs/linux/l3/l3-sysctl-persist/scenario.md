# Context — harden the kernel, permanently

A security scan flags this host: it forwards IP packets and accepts ICMP
redirects — neither is wanted on a normal server. Turn them off, at the kernel
level, so it holds now **and** after a reboot.

The point: a `sysctl` parameter can be changed live, but whatever is set live is
gone after a reboot. Making the setting active right now and making it durable
are two distinct moves: the tests will look at both.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/

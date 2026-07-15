# Context — harden the kernel, permanently

A security scan flags this host: it forwards IP packets and accepts ICMP
redirects — neither is wanted on a normal server. Turn them off, at the kernel
level, so it holds now **and** after a reboot.

Your mission, on the VM:

1. Set `net.ipv4.ip_forward = 0`.
2. Set `net.ipv4.conf.all.accept_redirects = 0`.
3. Make it **persistent** in `/etc/sysctl.d/` and apply it live
   (`sysctl --system`).

The point: `sysctl -w` changes a value now but loses it on reboot; a file in
`/etc/sysctl.d/*.conf` makes it durable, and `sysctl --system` re-reads all of
them. `sysctl -n <param>` reads the live value.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/

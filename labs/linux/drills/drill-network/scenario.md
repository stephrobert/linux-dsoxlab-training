# Context — the address that disappears

`ip addr add` works. The address is there, `ping` answers, you move on — and it
is gone at the next reload. It never existed anywhere but in the kernel's
memory.

Configuring the network means **declaring** it: to NetworkManager on RHEL, to
netplan on Debian. Same objective, two tools — so this drill exists once, and
its subject names neither.

**Stopwatch**: 4 tasks, 20 minutes, no hints. Everything is checked **after a
network reload**: what you typed by hand does not survive.

One rule above all: everything happens on the dedicated `lab0` interface.
**Never touch the management interface** — the one carrying your default route.
Its name changes with the provider and the distribution, which is exactly why
you identify it by what it does, not by what it is called. Cut it and you lose
the machine.

Read the subject: `dsoxlab challenge drill-network`.

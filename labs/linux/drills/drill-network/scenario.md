# Context — the address that disappears

An address set by hand works right away: it is there, `ping` answers, you move
on. And it is gone at the next reload. It had never existed anywhere but in the
kernel's memory.

Configuring the network means **declaring** it to the tool that owns it, and that
tool is not the same on RHEL and on Debian. Same objective, two implementations:
so this drill exists once, and its subject names neither.

**Stopwatch**: 4 tasks, 20 minutes, no hints.

Everything happens on the dedicated `lab0` interface. **Never touch the
management interface**, the one carrying your default route: its name changes
with the provider and the distribution, and if you cut it you lose the machine.

Read the subject: `dsoxlab challenge drill-network`.

# Context: the audit that finds eBPF wide open

Last week a contractor profiled an application on this server. Their tool ran
eBPF probes without being root, and to make that work someone relaxed the kernel
settings by hand, then forgot to put them back. The ticket is closed, the
contractor is gone, and this quarter's security audit has just landed: any
ordinary account on the machine can load code into the kernel, and the compiler
that turns those programs into processor instructions is not hardened.

This is not a detail. Several kernel flaws were only exploitable by an
unprivileged caller, and closing that door is one of the cheapest steps of Linux
hardening. But a kernel setting fixed at runtime is only fixed until the next
reboot, and whoever opened the door may also have left something that opens it
again.

What gets checked is the state of the machine: what the kernel applies right now,
what it really refuses to an unprivileged user, and what it will apply after a
reload of the configuration. Not the commands you typed.

Method in the companion guide:
https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/durcir-ebpf/

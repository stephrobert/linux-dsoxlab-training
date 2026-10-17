# Context: the program nobody deployed

During a security review, the team realises it does not know what this server's
kernel is running. eBPF probes are common here: systemd itself loads some to
filter the network and the devices of its services. But an eBPF program runs in
the kernel with extended rights, and whatever lands there without anybody having
decided it is exactly what an attacker settled on the machine would do to stay
discreet.

A colleague spotted a service with a bland name, something like "telemetry
collector", that nobody remembers deploying. The request is simple and precise:
say what is loaded, find what carries it, and if it has no business being there,
stop it for good, meaning the service must not come back at the next boot.
Without touching what the system loads by itself: an inventory that breaks the
machine is no better than the program it was looking for.

What gets checked is the state of the machine: what the kernel still holds,
whether the service can come back, and whether your answer names the service and
the type of the program correctly. Not the commands you typed.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/surface-attaque-bpf/

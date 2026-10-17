# Context: the process nobody recognises

A server in the house keeps writing to a file nobody can locate. The service in
charge is called `lab-mystere`, but the program running behind it carries a name
that neither the documentation nor the team recognises, and the file it feeds is
hidden somewhere on the disk. The usual tools do not show it: the file is only
open for an instant, then closed right away.

The kernel, however, saw everything. With eBPF you ask it to tell the story:
which programs are launched, which files are opened, and by whom. The point is
to find out the identity of the process and the target of its writes **without
stopping or changing it**: it is a production service, so you observe and you
do not touch.

What gets checked is the state of the machine: tracing tools that really work,
an answer that matches what is true on the machine, and a service left intact.
Not the commands you typed.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/ebpf/tracer/bpftrace/

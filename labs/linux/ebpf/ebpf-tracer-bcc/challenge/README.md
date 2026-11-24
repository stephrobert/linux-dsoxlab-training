# The process nobody recognises

## The situation

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
https://www.stephane-robert.info/en/docs/linux/going-deeper/ebpf/trace/bpftrace/

## What is asked

### Mission

A `lab-mystere` service runs a program whose name you do not know, and that
program writes every few seconds to a hidden file. Find both, with the eBPF
tracing tools, without stopping or changing the service.

### Goal (expected state)

1. A family of tracing tools is **installed and working** on the machine: the BCC
   tools (`bcc-tools` on AlmaLinux, `bpfcc-tools` on Ubuntu) or `bpftrace`.
2. The file `/var/tmp/reponse-ebpf.txt` contains a `binaire=` line giving the
   **name of the program** that writes. The bare name is enough; a full path
   ending with that name is accepted.
3. The same file contains a `fichier=` line giving the **full path** of the
   hidden file it writes to.
4. The `lab-mystere` service is still running, neither restarted nor modified.

Expected format of `/var/tmp/reponse-ebpf.txt`: two `key=value` lines, with no
space around the equal sign.

### Constraints

- The program and the file change at every `dsoxlab run`: an answer from a
  previous session is worthless.
- The file is only open for an instant: the kernel trace is the way to see it,
  reading the disk is not.
- Do not restart, kill or modify the service: treat it as a production service.
  Criterion 4 only counts once one of the tasks has succeeded.
- Loading an eBPF program needs root rights (`sudo`).
- Validation reads the state of the machine, not your command history.

### Validation

```bash
dsoxlab check ebpf-tracer-bcc                  # AlmaLinux 10 (default target)
dsoxlab check ebpf-tracer-bcc --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-tracer-bcc                  # a hint, at the cost of points
```

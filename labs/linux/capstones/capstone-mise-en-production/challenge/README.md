# The hand-over, then the morning after

## The situation

The two mock exams in this section assess a **certification**. This capstone
assesses something else: the ability to **deliver a server that holds**.

A learner who sits no certification deserves a final exercise too. This is it,
and it fits in one sentence: you are handed an application, you put it into
service, and **the machine reboots**.

## What the capstone actually measures

Nine deliverables, and a tenth test that covers them all at once. The mark
never depends on which commands you typed: every test reads an **observable
state**.

| Deliverable | What gets checked |
|---|---|
| Storage | a dedicated logical volume, mounted from `fstab` |
| Service account | system account, no login shell, owns the content |
| Service | active, `enabled`, listening on the network |
| MAC | SELinux enforcing, port labelled, context durable |
| Firewall | port opened permanently |
| Access | a 200 obtained **from another machine** |
| Journal | persisted on disk |
| SSH | neither password nor root |
| Backup | scheduled, and has already produced an archive |

## The reboot, and why it is worth 10 points

A server that works on hand-over day and not the next morning was never put
into production. The four omissions that produce that outcome are always the
same, and none of them shows before the reboot:

1. the mount is not in `fstab`;
2. the service was never switched to `enabled`;
3. the firewall rule was added without `--permanent`;
4. the SELinux label comes from a `chcon` instead of `semanage`.

So the last test reboots the machine for real, then asks for the page again
**from the client**. If it comes back, all four are right at once.

## Three traps specific to this machine, measured

Port **8080 does not belong** to `http_port_t` on AlmaLinux 10: the default
list is 80, 81, 443, 488, 8008, 8009, 8443, 9000. The service will refuse to
start, with a permission message that never names SELinux.

`/var/log/journal` **does not exist**: while it is missing, journald keeps
everything in memory and the history disappears on reboot.

The `sshd` configuration is **split across several files**. Writing your own
is not enough: `sshd` keeps the **first** value it reads, in the lexical order
of the files. `sshd -T` tells you the effective configuration; the file you
have just written only tells you your intentions.

## Capstone: put a server into production

**Format**: 1 mission, 10 tests, 100 points, 2 VMs, 90 minutes.
**Pass mark**: 80/100. **No hints** will be given.

### The mission

The development team has delivered the **cotisation** application in
`/opt/livraison` on `alma-rhcsa-1.lab`. It contains a page, a `VERSION` file
and an operating note.

> Put it into service. It must answer over HTTP on port **8080**, be reachable
> from `alma-rhcsa-2.lab`, and **everything must come back after a reboot**.

Read `/opt/livraison/LISEZ-MOI.txt`: the operating constraints are in there.

### Your machines

| Host | Role |
|---|---|
| `alma-rhcsa-1.lab` | AlmaLinux 10 — the server to put into production, free disk `/dev/vdb` |
| `alma-rhcsa-2.lab` | AlmaLinux 10 — the client, where the verdict is taken |

Connection: `dsoxlab ssh alma-rhcsa-1.lab`. You are `student`, with passwordless
sudo.

### What is marked

| Points | What the test observes |
|---|---|
| 15 | The content lives on a **dedicated logical volume**, mounted persistently |
| 10 | The service runs under a **system account** with no login shell |
| 15 | The service is **active**, **enabled**, and listening on the network |
| 15 | SELinux **enforcing**, port **labelled**, content context **durable** |
| 10 | The firewall opens the port **permanently** |
| 15 | The **client** gets a 200 and the right page |
| 5 | The **journal** survives a reboot |
| 5 | `sshd` refuses **passwords** and the **root account** |
| 10 | A **scheduled backup** exists and has already produced an archive |
| 10 | **Everything comes back after a real reboot** |

### The last test really reboots the machine

This is not a formality. Putting a server into production is judged on what
**comes back on its own**. Four classic omissions only show at reboot time:

- a mount missing from `/etc/fstab`;
- a service never switched to `enabled`;
- a firewall rule added without `--permanent`;
- a SELinux label set with `chcon` rather than `semanage`.

The test reboots the server, then asks for the page again **from the client**.
If it comes back, all four are right. If not, the delivery is refused.

### Three traps measured on this machine

Port **8080 does not belong** to `http_port_t` on AlmaLinux 10. The ports
already allowed are 80, 81, 443, 488, 8008, 8009, 8443 and 9000. Without
`semanage port`, the service cannot bind to it, and the error message will
talk about permissions, not about SELinux.

`/var/log/journal` **does not exist** at the start: journald keeps everything
in memory and loses the history at every reboot, which is precisely when you
would need it.

The `sshd` configuration arrives **split across several files**, as on any
recent server. Writing your own therefore does not guarantee that it applies:
`sshd` keeps the **first** value it reads, and the files are read in lexical
order. The only check that counts is `sshd -T`, which prints the **effective**
configuration, not the one you have just written.

### Method

The order that works is an operator's order: **storage** first, since
everything sits on it; the **service** next; the **protections** after that,
because you only open what must be open; the **backup** last, because it backs
up a state that exists.

Validation: `dsoxlab check`.

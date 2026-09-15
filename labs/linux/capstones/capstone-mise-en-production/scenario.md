# Context: the hand-over, then the morning after

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

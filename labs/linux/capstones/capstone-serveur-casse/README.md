# Capstone: broken server

**Format**: 1 symptom, 7 tests, 100 points, 2 VMs, 45 minutes.
**Pass mark**: 80/100. **No hints** will be given.

## The symptom

> The internal site hosted on `alma-rhcsa-1.lab` does not answer any more.
> Users, who reach it from `alma-rhcsa-2.lab`, get nothing.
>
> Over to you.

That is all you get. The site was working a few minutes ago.

## Your machines

| Host | Role |
|---|---|
| `alma-rhcsa-1.lab` | AlmaLinux 10 — the broken server |
| `alma-rhcsa-2.lab` | AlmaLinux 10 — the client, where the verdict is taken |

Connect with `dsoxlab ssh alma-rhcsa-1.lab`. You are `student` with sudo
NOPASSWD.

**The verdict is taken from the client.** A `curl localhost` answering 200 on
the server proves nothing: that is exactly what happens when the service only
listens on loopback, or when the firewall closed the port. Test like a user.

## What is scored

| Points | What the test observes |
|---|---|
| 30 | The client gets a **200** and the right page |
| 10 | The service is **active** and **enabled** |
| 10 | It listens on the network, not only locally |
| 10 | The firewall is **running** and the port is **permanently** open |
| 15 | SELinux is **still enforcing** |
| 15 | The context of the served content is **durable** |
| 10 | The docroot is **not** world-writable |

## The three traps that cost you the capstone

They make the site answer, and they score zero:

1. `setenforce 0` or `SELINUX=permissive`;
2. `systemctl stop firewalld`;
3. `chmod -R 777` on the docroot.

Those are not repairs, they are security regressions. This capstone exists
precisely to tell the difference.

## Persistence

Anything that would not survive a reboot scores zero. One case deserves your
attention: `chcon` fixes the **current** SELinux context and even survives a
reboot, but a system relabel wipes it. The tests run `restorecon` before
concluding: only a `semanage fcontext` rule holds.

## Method

No method is imposed. The one that works, however, always starts with
**observing before modifying**:

```text
confirm the symptom from the client
        |
observe the server state, changing nothing
        |
form ONE hypothesis
        |
check it, then fix that one thing
        |
re-test from the client
```

Final validation: `dsoxlab check`.

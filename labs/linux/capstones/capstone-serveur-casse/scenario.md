# Context: a fault that will not name itself

This capstone is not one more troubleshooting lab. The section already has
several, and they share one flaw: their title hands you half the diagnosis.
"Fix a SELinux problem" has already told you where to look.

Here you get a **symptom**, and nothing else:

> The internal site does not answer any more.

The setup built a site that **worked**, proved it, then broke **one single
thing**, drawn at random from six. Nobody will tell you which. That is the
difference between following a procedure and knowing how to troubleshoot.

## The six possible faults

They are listed here only so you know the list is **finite**, and that none of
them is exotic. All of them produce the same symptom seen from the client.

| Family | What you need to look at |
|---|---|
| Service | unit state, and whether it persists |
| Port | what listens, and on which address |
| Firewall | what is open, and permanently or not |
| SELinux | the context of the served content |
| Permissions | directory traversal and file read |
| Local-only listen | the listening address, not just the port number |

A seventh fault was dropped after measurement: filling the disk does **not**
stop a static site. Serving a file requires no write.

## The rule that makes this exercise worth doing

Three repairs "work" and score **zero**:

- putting SELinux into permissive mode;
- stopping the firewall;
- making the docroot world-writable.

Each one makes the site answer, and each one disarms a protection covering the
whole machine to solve a local problem. A server that answers because it is no
longer protected is not repaired.

## Persistence

Anything that would not survive a reboot scores zero. Watch out for the SELinux
case: a `chcon` survives a reboot, but **not a relabel**. The tests run
`restorecon` before concluding.

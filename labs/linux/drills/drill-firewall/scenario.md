# Context — the firewall, and the rule that vanishes

Every RHCSA candidate has done it: open the port, test it, it works, move on —
and lose the points, because the rule was never made permanent. It lived in
memory and died at the first reload.

This drill is a **stopwatch**: 5 tasks, 20 minutes, no hints. The objective is
the same on both certifications; only the tool changes — `firewalld` on RHEL,
`ufw` on Debian. So the subject names neither.

Two things are being measured beyond the commands:

- **persistence** — your rules are checked *after a reload*. What does not
  survive does not count;
- **not locking yourself out** — you work over SSH. A firewall that comes up
  without SSH allowed costs you the machine, and every remaining task with it.

Read the subject: `dsoxlab challenge drill-firewall`.

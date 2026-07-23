# Context — SELinux, and what does not survive

The reflex that fails RHCSA candidates: flip SELinux into enforcing on the fly,
and move on. It works, until the reboot. Same story with a file context set by
hand: the service starts, all is well, and the first relabel wipes it.

SELinux has a **runtime** and a **policy**. What you change at runtime is
temporary, what you write into the policy survives. Every task in this drill is
built on that distinction.

This drill is a **stopwatch**: 4 tasks, 20 minutes, no hints. RHCSA only; Debian
has AppArmor, an entirely different model, drilled in `drill-apparmor`.

Read the subject: `dsoxlab challenge drill-selinux`.

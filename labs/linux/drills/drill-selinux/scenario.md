# Context — SELinux, and what does not survive

The reflex that fails RHCSA candidates: `setenforce 1` and move on. It works —
until the reboot. Same with `chcon`: the context is right, the service starts,
and the first relabel wipes it.

SELinux has a **runtime** and a **policy**. What you change at runtime is
temporary. What you write into the policy survives. Every task in this drill is
built on that distinction.

This drill is a **stopwatch**: 4 tasks, 20 minutes, no hints. RHCSA only —
Debian has AppArmor, an entirely different model, drilled in `drill-apparmor`.

Your contexts are checked **after a relabel**. Choose your tool accordingly.

Read the subject: `dsoxlab challenge drill-selinux`.

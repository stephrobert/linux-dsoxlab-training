# Context — systemd, against the clock

`systemd` is where a Linux administrator spends their days: a service that must
come back, a job that must run at the right time, a unit that must never start
again. At the exam, none of this is the question — it is the **tooling** you
answer with.

This drill is a **stopwatch**: 5 tasks, 25 minutes, no hints. The same skills
serve RHCSA and LFCS: systemd is systemd on RHEL and on Debian.

Three traps you will meet again:

- **`enabled` and `running` are two different things**: a service can run today
  and be gone after a reboot;
- **`disable` does not prevent starting** — only `mask` does;
- a **timer** needs its `.service`: the two go together.

Read the subject: `dsoxlab challenge drill-systemd`.

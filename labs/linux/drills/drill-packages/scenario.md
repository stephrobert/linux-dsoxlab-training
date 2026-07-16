# Context — the same job, two tools

RHCSA and LFCS ask the same thing of you: install, freeze, query, remove. Only
the tool changes — `dnf` on RHEL, `apt` on Debian. That is exactly why this
drill exists **once**, and why its subject never names the command: an
administrator knows the objective, then reaches for the tool their distribution
provides.

This drill is a **stopwatch**: 5 tasks, 20 minutes, no hints.

What is being measured:

- **installing** and **removing** — the easy part;
- **freezing** a package, so that no upgrade moves it. This is what you do to a
  version your application depends on;
- the two **queries** that save you at the exam: *which package provides this
  file?* and *what did this package install?*

Read the subject: `dsoxlab challenge drill-packages`.

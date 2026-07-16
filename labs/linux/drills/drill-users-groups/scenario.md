# Context — the account lifecycle, against the clock

Creating a user is trivial. Creating **the right** user, with the right UID, the
right groups, an aging policy that actually applies, a delegation that grants
exactly what is needed and nothing more, and closing an account so that it is
truly closed — that is the job.

This drill is a **stopwatch**: 5 tasks, 20 minutes, no hints. The same skills
serve RHCSA and LFCS — `useradd`, `usermod`, `chage` and `sudoers` behave
identically on RHEL and Debian.

Two traps you will meet again at the exam:

- an account that expires is **not** the same thing as a password that expires;
- locking a password does **not** close an account: the shell must forbid login
  too, otherwise an SSH key still gets in.

Read the subject: `dsoxlab challenge drill-users-groups`.

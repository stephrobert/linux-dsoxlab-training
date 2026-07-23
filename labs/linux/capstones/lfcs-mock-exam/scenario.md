# Context — the LFCS exam, under exam conditions

This capstone is not a lab: it is a **mock exam**. No hints, no step-by-step, a
clock, and a passing score. It covers the **5 official LFCS domains** in their
real weights:

| Domain | Weight | Tasks |
|---|---|---|
| Essential Commands | 20% | 1–4 |
| Operations Deployment | 25% | 5–8 |
| Users and Groups | 10% | 9–10 |
| Networking | 25% | 11–14 |
| Storage | 20% | 15–17 |

**17 tasks, 100 points, 120 minutes, 70/100 to pass.**

Everything happens on a single Ubuntu 24.04 VM — the LFCS is multi-distro, and
this run is the Debian side of it.

The rule that fails candidates: **persistence**. Whatever vanishes at reboot
scores zero. The tests read the state of the system, not the commands you typed.

Read the subject: `dsoxlab challenge lfcs-mock-exam`.

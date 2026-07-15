# Capstone — RHCSA EX200 mock exam

> Prepare the 2 VMs: `dsoxlab run rhcsa-mock-exam`

## Format

- **20 tasks, 100 points, 2 VMs, 180 minutes.** Passing score: **70/100**.
- **No hints** are revealed for this capstone.
- Everything must be **persistent after reboot**: a live-only change that is lost
  after a reboot scores nothing. Reboot both VMs before validating.

## Machines

| Target | Host | Scope |
|---|---|---|
| `server` | `alma-rhcsa-1.lab` | 16 tasks — storage, services, SELinux, NFS export |
| `client` | `alma-rhcsa-2.lab` | 4 tasks — NFS mount, SSH key auth, root recovery |

`dsoxlab run` provisions the exam **givens**: the extra disk `/dev/vdb`, an
existing `/var/log/myapp.log`, a mislabeled `/var/www/html/index.html`, and a
randomized root password on the client (for the `rd.break` recovery task).

## Run and validate

```bash
dsoxlab run rhcsa-mock-exam        # bring up the 2 VMs and the exam givens
dsoxlab challenge rhcsa-mock-exam  # read the full 20-task mission
# … perform the tasks on the VMs, then reboot both …
dsoxlab check rhcsa-mock-exam      # real-time score, not recorded
dsoxlab submit rhcsa-mock-exam     # final submission, recorded in history
```

The validation asserts the **observable state** of each machine, not the path
you took. The full mission is in [`challenge/README.md`](./challenge/README.md).

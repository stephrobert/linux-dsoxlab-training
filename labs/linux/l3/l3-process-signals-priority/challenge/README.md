# Make the batch job get out of the way

## The situation

A background worker (`labworker.service`) runs flat out at normal priority and
makes the box feel sluggish for everyone else. Give it a **nice value of 10** so
the scheduler lets interactive work go first — and make that stick across
restarts.

The point: a process's priority is set when it starts, and can be corrected on
the fly on a process already running. But a systemd-managed service starts over
from its definition on every restart: an on-the-fly correction does not survive
it.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/processes/

## What is asked

### Mission

Lower the priority of the `labworker` service to nice 10, persistently.

### Goal (expected state)

1. The `labworker` service is running.
2. Its process runs at **nice 10** (`ps -o ni= -p <MainPID>`).
3. `Nice=10` is set in the unit or a drop-in (persistence).

### Constraints

- Ideally `systemctl edit labworker` (drop-in), then `daemon-reload` + restart.
  Validation reads the process's **live priority**, not the command.

### Validation

```bash
dsoxlab check l3-process-signals-priority
```

# Challenge — l3-process-signals-priority

## Mission

Lower the priority of the `labworker` service to nice 10, persistently.

## Goal (expected state)

1. The `labworker` service is running.
2. Its process runs at **nice 10** (`ps -o ni= -p <MainPID>`).
3. `Nice=10` is set in the unit or a drop-in (persistence).

## Constraints

- Ideally `systemctl edit labworker` (drop-in), then `daemon-reload` + restart.
  Validation reads the process's **live priority**, not the command.

## Validation

```bash
dsoxlab check l3-process-signals-priority
```

# Challenge — l3-scheduling-at

## Mission

Schedule `touch /run/rapport.done` to run once, later, with `at`.

## Goal (expected state)

1. `atd` is running.
2. A job is queued (`atq` not empty), scheduled in the future.
3. The queued job runs `touch /run/rapport.done` (`at -c <n>`).

## Constraints

- Use `at` (not cron): the job must be one-shot.
- Validation reads `atq` and the job's script, not your history.

## Validation

```bash
dsoxlab check l3-scheduling-at
```

# Run something once, later

## The situation

Cron repeats a job on a schedule. But sometimes you want a command to run
**once**, at a specific time, and never again — a maintenance action tonight, a
reminder in an hour. That's what **`at`** is for.

The point: a one-shot job is put in a queue, then handed to a daemon that will
run it at the stated time and forget it. Unlike cron it does not repeat, and
nothing runs at all if that daemon is not running.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/operate/scheduling/at/

## What is asked

### Mission

Schedule `touch /run/rapport.done` to run once, later, with `at`.

### Goal (expected state)

1. `atd` is running.
2. A job is queued (`atq` not empty), scheduled in the future.
3. The queued job runs `touch /run/rapport.done` (`at -c <n>`).

### Constraints

- Use `at` (not cron): the job must be one-shot.
- Validation reads `atq` and the job's script, not your history.

### Validation

```bash
dsoxlab check l3-scheduling-at
```

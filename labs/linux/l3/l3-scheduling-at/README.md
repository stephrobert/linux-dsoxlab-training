# Lab — one-shot scheduling with at

> Prepare: `dsoxlab provision` then `dsoxlab run l3-scheduling-at`

## Recap

[**at on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/)

`at` queues a command to run **once** at a later time, handled by `atd`. Feed the
command on stdin: `echo 'cmd' | at <time>`. `atq` lists pending jobs, `at -c <n>`
prints a job's script, `atrm <n>` removes it. Unlike cron, it does not repeat.

## Objectives

- `atd` is running;
- a job is queued (`atq` is not empty);
- that job runs `touch /run/rapport.done`.

## Validate

```bash
dsoxlab check l3-scheduling-at
```

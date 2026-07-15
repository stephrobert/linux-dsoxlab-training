# Lab — process priority with Nice

> Prepare: `dsoxlab provision` then `dsoxlab run l3-process-signals-priority`

## Recap

[**Processes on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/comprendre-processus/)

Nice values run from `-20` (highest priority) to `19` (lowest). `nice -n N cmd`
starts a process at a priority, `renice N -p PID` changes a running one. For a
service, `Nice=` in the unit (or a `systemctl edit` drop-in) makes it durable.
Signals — `kill -TERM/-HUP/-9` — control running processes. `ps -o ni -p <pid>`
shows the current nice.

## Objectives

- `labworker.service` runs at **nice 10** (drop-in `Nice=10`, reload, restart);
- proven on the live process and in the unit config.

## Validate

```bash
dsoxlab check l3-process-signals-priority
```

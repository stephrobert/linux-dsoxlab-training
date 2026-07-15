# Lab — Diagnose a systemd service stuck in a crash loop

> 💡 **Coming directly to this lab?** Each lab is **self-contained**.
> Single requirement: the 3 lab VMs must be running and accessible via
> SSH+sudo.
>
> ```bash
> cd /home/bob/Projets/linux-training
> make verify-conn   # → 3 hosts respond on SSH+sudo
> ```
>
> If KO, run `make bootstrap && make provision` from the repo root.

## 🧠 Reminder

🔗 [**Diagnose a crashed systemd service**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/services-processus/service-crash-loop/)

A `Restart=always` service can enter a **crash loop** when its
`ExecStart` fails reproducibly: missing config, missing binary,
unsatisfied dependency, port already taken. Diagnosis always follows the
same chain:

1. `systemctl status <svc>` → state + last journal lines + ExecStart
   exit code.
2. `journalctl -u <svc> --since '1h ago'` → full logs, scroll up to the
   **first** failure.
3. Hypothesis → targeted check → fix → `daemon-reload` if the unit was
   modified → `restart` → `is-active` + `is-enabled`.

The **method** matters, not the specific fix command.

## 🎯 Objectives

By the end of this lab, you will know how to:

- Identify a service in a **crash loop** (vs simply stopped or
  permanently failed).
- Read `systemctl status` to distinguish **PID exit code**, **journal
  tail**, and **restart counter**.
- Find the **root cause** via `journalctl -u <svc>` (`-b`, `--since`,
  `--no-pager`).
- Distinguish a **temporary** fix (`systemctl restart`) from a
  **durable** one that survives a reboot (the RHCSA
  `persistence_after_reboot` criterion).
- Apply the rule: **`daemon-reload`** every time you touch a unit file.

## 🔧 Setup

The broken service must already be in place on the target VM. On the
trainer side, that's done by `runtime/kvm.sh` (run by `dsoxlab run` or
`make setup`).

On the learner side — `dsoxlab run` already opens your SSH session
on the target VM. To reconnect later:

```bash
dsoxlab ssh alma-rhcsa-1
```

Once on the VM, confirm the service is actually crash-looping:

```bash
systemctl is-active demo-crashloop.service
# Expected: "activating" or "failed" (the loop runs ~ every 2s).
```

## 📚 Exercise 1 — Confirm the crash loop

Run:

```bash
sudo systemctl status demo-crashloop.service
```

**Expected** (excerpt):

```text
● demo-crashloop.service - Demo service stuck in crash loop (lab depanner/services-processus)
     Loaded: loaded (/etc/systemd/system/demo-crashloop.service; enabled; preset: disabled)
     Active: activating (auto-restart) (Result: exit-code) since ...; 1s ago
   Main PID: ... (code=exited, status=1/FAILURE)
   ...
```

### 🔍 Observation

Three converging hints:

- **`Active: activating (auto-restart)`** — the service is **not
  stable**; systemd is between two attempts.
- **`Result: exit-code`** with **`status=1/FAILURE`** — the binary dies
  with non-zero exit code. Not a system kill.
- The **`Main PID`** changes between runs (re-run twice to see).

That's the classic crash-loop signature. Now find **why** the binary
fails.

## 📚 Exercise 2 — Root cause via journalctl

`systemctl status` only shows the last 10 journal lines. For the
**first** cause, scroll up with `journalctl`:

```bash
sudo journalctl -u demo-crashloop.service -b --no-pager | head -30
```

**Expected** (excerpt):

```text
... demo-crashloop[...]: FATAL: Configuration file not found: /etc/demo-crashloop/config.yml
... demo-crashloop[...]:        Service cannot start without configuration.
... systemd[1]: demo-crashloop.service: Main process exited, code=exited, status=1/FAILURE
... systemd[1]: demo-crashloop.service: Failed with result 'exit-code'.
... systemd[1]: demo-crashloop.service: Scheduled restart job, restart counter is at N.
```

### 🔍 Observation

The **first** message says it all: the daemon is looking for
`/etc/demo-crashloop/config.yml`, which doesn't exist. No need to
investigate further before clearing this cause.

Verify:

```bash
ls -la /etc/demo-crashloop/ 2>&1
# Output: "ls: cannot access '/etc/demo-crashloop/': No such file or directory"
```

## 📚 Exercise 3 — Read the unit file to understand the contract

Before creating the config file, see what the binary expects exactly.
The unit tells you where the binary is:

```bash
sudo systemctl cat demo-crashloop.service
```

You'll see `ExecStart=/usr/local/bin/demo-crashloop`. Read that binary:

```bash
sudo cat /usr/local/bin/demo-crashloop
```

The script expects:

- A file `/etc/demo-crashloop/config.yml`
- A line `port: <number>` inside (parsed by awk)
- Otherwise it exits with code 1 or 2.

### 🔍 Observation

Typical of poorly documented apps: the error doc is in the code. Always
read the `ExecStart` binary/script when `journalctl` mentions a missing
file.

## 📚 Exercise 4 — Durable fix

Three steps for a **persistent** fix:

### 4.1 Create the directory and config file

```bash
sudo mkdir -p /etc/demo-crashloop
sudo tee /etc/demo-crashloop/config.yml >/dev/null <<'EOF'
port: 8080
EOF
sudo chmod 0644 /etc/demo-crashloop/config.yml
sudo chown root:root /etc/demo-crashloop/config.yml
```

> **Security**: `chmod 0644` quoted, `chown root:root` explicit. This
> aligns with the repo's "security by default" rule — a config file
> must never inherit the current user.

### 4.2 Restart the service

```bash
sudo systemctl restart demo-crashloop.service
```

No `daemon-reload` needed (we did **not** touch the unit file — only
created the config it was waiting for).

### 4.3 Verify persistence

```bash
sudo systemctl is-active demo-crashloop.service   # → active
sudo systemctl is-enabled demo-crashloop.service  # → enabled
sudo systemctl status demo-crashloop.service | head -5
```

### 🔍 Observation

- `is-active` must return **`active`** (not `activating` or `failed`).
- `is-enabled` must return **`enabled`** — that's what guarantees the
  service comes back after reboot. This is the
  `persistence_after_reboot: true` criterion validated by the tests.

## 🔍 Things to notice

- **`Restart=always` hides real errors**: a hurried operator just sees
  "the service is UP some of the time" and moves on. The
  `journalctl --since '1h ago'` method is non-negotiable.
- **Root cause is always in the FIRST error message** — scroll up, not
  down.
- **`daemon-reload` after editing a unit, not after editing the
  application config** — RHCSA-relevant distinction.
- **`is-active` + `is-enabled`**: both are needed for reboot
  persistence. Missing `is-enabled` is the classic RHCSA junior
  mistake.

## 🤔 Reflection questions

1. If the service restarted properly but exited after 30 minutes (vs
   instantly), how would you adapt your diagnosis? Which extra tools
   (e.g. `coredumpctl`, `systemd-analyze blame`)?

2. You find the service crash-looping on **3 identical servers** in
   parallel. What remediation strategy (local vs Ansible automation)?
   What should be documented before touching anything?

3. How could this crash loop have been **prevented**? (Hints:
   `validate=` in Ansible, `systemd-analyze verify`, declared
   dependency `Requires=` or `ConditionPathExists=` in the unit.)

## 🚀 Final challenge

See [`challenge/README.md`](challenge/README.md). The challenge asks
you to **diagnose and fix** the crash-looping service directly on
the VM, in your interactive session — no script to write. Validation
via `dsoxlab check` runs pytest+testinfra against the VM's final
state.

## 💡 Going further

- **`coredumpctl list`** + `coredumpctl info <pid>`: for services that
  crash with a signal (SIGSEGV, SIGABRT) instead of an exit code.
- **`systemd-analyze blame`** + `critical-chain`: identify services
  that slow down boot (useful for the `depanner/demarrage/`
  subsection).
- **Drop-in override** in `/etc/systemd/system/<svc>.d/override.conf`
  to change `Restart`, `RestartSec`, or `ExecStartPre` without
  modifying the main unit.
- **`journalctl -p err -b -u <svc>`** filters by priority (warning,
  err, alert, crit) — saves time when the service is verbose.

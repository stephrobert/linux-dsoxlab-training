# SELinux, and what does not survive

## The situation

The reflex that fails RHCSA candidates: flip SELinux into enforcing on the fly,
and move on. It works, until the reboot. Same story with a file context set by
hand: the service starts, all is well, and the first relabel wipes it.

SELinux has a **runtime** and a **policy**. What you change at runtime is
temporary, what you write into the policy survives. Every task in this drill is
built on that distinction.

This drill is a **stopwatch**: 4 tasks, 20 minutes, no hints. RHCSA only; Debian
has AppArmor, an entirely different model, drilled in `drill-apparmor`.

Read the subject: `dsoxlab challenge drill-selinux`.

## Drill — SELinux

**Format**: 4 tasks, 100 points, 20 minutes. **No hints.**

```bash
dsoxlab check drill-selinux
```

SELinux is currently in **permissive**, a context is wrong, a boolean is off.

---

### Task 1 — Enforcing, for good (25 pts)

SELinux must be **enforcing now**, and still be after a **reboot**.

### Task 2 — The right context (25 pts)

`/srv/web/index.html` must carry the **`httpd_sys_content_t`** context — and
keep it **after a relabel**.

### Task 3 — The boolean (25 pts)

**`httpd_can_network_connect`** must be **on**, and stay on after a reboot.

### Task 4 — A non-standard port (25 pts)

Port **`8888/tcp`** must carry the **`http_port_t`** label, so a web service can
bind to it.

---

**Your contexts are checked after a relabel.** What the policy does not know
does not survive.

## Validate

```bash
dsoxlab check drill-selinux
```

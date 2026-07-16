# Drill — SELinux

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

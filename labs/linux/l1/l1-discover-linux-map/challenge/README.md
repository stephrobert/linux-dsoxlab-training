# Map the machine before touching it

## The situation

This is your first Linux box, and you do not yet know what runs on it. Before
configuring anything, an administrator answers four questions: which kernel,
which distribution, where the configuration files live, where the logs live. As
long as those answers stay vague, everything that follows is vague too.

This lab does not ask you to recite definitions, it asks you to record four
**real** facts about your own machine. Validation compares them to the state of
the system: a value copied from a tutorial fails.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/discover-linux/linux-basics/

## Map your Linux system

Work in **`challenge/work/`** — the file `notions.md` was created there by
`dsoxlab run`. Complete it without a step-by-step guide.

---

### Mission

You are setting up your first Linux workstation. Before touching anything, you must
know what you are working on. **Explore your machine** and record four
real facts in `notions.md`:

1. `KERNEL` — your kernel version, via `uname -r`.
2. `DISTRO_ID` — your distribution's identifier, in `/etc/os-release`.
3. `ETC_FILE` — the name of **one** file actually present in `/etc`.
4. `LOG_FILE` — the name of **one** file actually present in `/var/log`.

### Constraints

- Each field must contain the **real value from your machine**, not an example.
  Validation compares your answers against the real system state: an
  invented value fails.
- All `<value>` placeholders must be replaced.

### Useful commands

```bash
uname -r
grep '^ID=' /etc/os-release
ls /etc
ls /var/log
```

### Validation

```bash
dsoxlab check l1-discover-linux-map   # valide ton travail
dsoxlab hint  l1-discover-linux-map   # bloqué ? un indice (coûte des points)
```

> The **concepts** (what a kernel is for, how a distribution differs from
> the kernel, the role of `/etc` and `/var/log`) are covered in the course and checked
> by the associated quiz. This lab proves that you have actually explored your
> system.

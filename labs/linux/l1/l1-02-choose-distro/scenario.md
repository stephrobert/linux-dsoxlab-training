# Lab l1-02 — Choose your reference Linux distribution

| | |
|---|---|
| **Level** | L1 — Fundamentals (B0) |
| **Runtime** | `shell` — no VM required |
| **Estimated time** | 15 min |
| **Reference** | [Choisir sa distribution Linux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions/) |

---

## What you will learn

By the end of this lab you will be able to:

- Name the two main Linux distribution families and their package managers
- Describe at least two criteria for choosing a distribution
- Match a distribution to a specific use case: learning, certification, home server
- Explain why choosing a distribution matters at the start of a Linux journey

---

## The two great families

Linux distributions are not all equal. They differ in their package manager,
default tools, release cycle and target audience.

### Debian / Ubuntu family

| Criterion | Debian | Ubuntu LTS |
|-----------|--------|------------|
| Package manager | `apt` / `.deb` | `apt` / `.deb` |
| Release cycle | ~2 years (very stable) | 2 years LTS (5-year support) |
| Target | Servers, advanced users | Beginners, workstations, servers |
| Community | Huge, long-standing | Huge, very active |
| Certification target | General Linux | General Linux |

Key commands to remember:

```bash
apt search <package>
apt install <package>
apt update && apt upgrade
```

### RHEL family (Red Hat Enterprise Linux)

| Criterion | AlmaLinux / Rocky Linux | RHEL |
|-----------|------------------------|------|
| Package manager | `dnf` / `.rpm` | `dnf` / `.rpm` |
| Release cycle | ~5-year aligned with RHEL | ~5 years |
| Target | Servers, enterprise, certification prep | Enterprise production |
| Community | Active (RHEL rebuilds) | Commercial (subscription) |
| Certification target | **RHCSA**, **RHCE** | **RHCSA**, **RHCE** |

Key commands to remember:

```bash
dnf search <package>
dnf install <package>
dnf check-update && dnf update
```

---

## Three scenarios — which distribution?

Read each scenario below. Then fill in `choix-distro.txt` with your choice and a justification.

There is no single correct answer. What matters is your reasoning.

---

### Scenario A — Complete beginner

> You have never used Linux. You want to learn the basics: the terminal, files, users,
> services. You have a spare laptop. You will mostly follow tutorials from the web.

**Think about:**
- Which distribution has the most beginner-friendly documentation?
- Which one is most likely to be covered in the tutorials you will find?
- Which package manager is easier to discover first?

---

### Scenario B — RHCSA preparation

> You want to pass the RHCSA exam (EX200) within 6 months.
> You need a free lab environment at home that behaves exactly like RHEL.

**Think about:**
- Which distributions are binary-compatible rebuilds of RHEL?
- Does the package manager matter for the exam?
- Does the version (RHEL 9, RHEL 10) matter?

---

### Scenario C — Personal test server

> You have a small VM or a Raspberry Pi at home. You want to host a few services:
> a web server, a database, a reverse proxy. The server must be stable and low-maintenance.

**Think about:**
- Which distribution prioritises stability over latest features?
- How long is the support window?
- Do you need commercial support?

---

## Fill in your answer file

Open the answer file and fill in each section:

```bash
cat challenge/work/choix-distro.txt        # read the template
nano challenge/work/choix-distro.txt       # fill it in
```

```bash
dsoxlab check l1-02-choose-distro   # validate when done
```

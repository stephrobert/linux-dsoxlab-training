# Lab — choosing your server distribution

## Reminder

[**Choosing a Linux server distribution**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions-serveur/)

In a server context, two families dominate: the **Debian** family (Debian,
Ubuntu Server) and the **Red Hat** family (RHEL, Rocky Linux, AlmaLinux). The
guide compares them to cars: the engine, the Linux kernel, is the same; the
dashboard, the administration tools and the location of certain files change
depending on the manufacturer.

What "kernel", "distribution" and "family" mean precisely is covered in
`l1-discover-linux-map`: none of that is repeated here. This lab starts from
the following question, the one that really comes up the day you build a
server: **on what criteria do you decide, and what do you sign up to by
deciding?**

## The course

The measurements reproduced below deliberately deal with something other than
the challenge: they query **package repositories** and the **security state** of
a workstation, never the identity of the system. They come from an
**Ubuntu 24.04.2 LTS** workstation (kernel `6.8.0-134-generic`), and **the
machine on which you play this lab may not be from the same family**. None of
them requires `sudo`, none installs or modifies anything: run them on your own
machine and compare.

Everything that cannot be measured from a workstation (life cycles, prices,
governance) comes from two pages of the guide, cited each time: the reference
page linked above and the comparison
[Debian vs Ubuntu vs AlmaLinux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/distributions/comparatif/).

### The criterion that really decides: the duration, and above all the scope

Choosing a distribution is not choosing a logo, it is **signing a support
contract**. That contract has two terms, and almost every comparison only
mentions one.

The first term, the one everyone publishes, is the **duration**. Here is what
the projects announce, as the guide's comparison records it:

| Distribution | Free support | Detail of the cycle |
|---|---|---|
| Debian 13 | 5 years | 3 years of full support (until 9 August 2028), then 2 years of LTS (until 30 June 2030) |
| Ubuntu 26.04 LTS | 5 years | standard maintenance of `main` until 2031 |
| AlmaLinux 10 | 10 years | active support until 31 May 2030, security fixes until 31 May 2035 |

The second term, the one nobody publishes, is the **scope**: the list of
packages the vendor really commits to fixing. And that is the one that decides,
because a number of years without a scope means nothing.

That scope can be measured, without special privileges. On a machine from the
Debian family, `apt-cache policy` tells you from **which repository** each
version of a package comes:

```bash
apt-cache policy nginx fail2ban
```

```text
nginx:
  Candidate: 1.24.0-2ubuntu7.15
     1.24.0-2ubuntu7.15 500
        500 http://fr.archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
        500 http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
[...]
fail2ban:
  Candidate: 1.0.2-3ubuntu0.1
     1.0.2-3ubuntu0.1 500
        500 http://fr.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages
[...]
```

Two packages, two contracts. `nginx` comes from **`main`** and its latest
version is served by **`noble-security`**, the proof that a fix is published
there for it. `fail2ban` comes from **`universe`**: the guide recalls that
Canonical's free commitment covers `main` only, `universe` being covered "best
effort", with no commitment, and **from day one**. A server exposed on the
Internet that relies on `fail2ban` therefore relies on a package outside the
contract.

> **A nuance observed on the machine, and absent from the guide.** On that same
> workstation, `apt-cache policy docker.io` shows a version served by
> `security.ubuntu.com noble-security/universe`: a package from `universe`
> **can** therefore receive an update through the security channel. There is
> simply **no guarantee** that it will receive one, and `fail2ban` as well as
> `certbot`, measured in the same second on the same machine, have none. "No
> commitment" does not mean "never fixed", it means "nothing to hold the vendor
> to the day it is not".

Remember the method more than the result: before choosing, list the five or six
packages that really carry your service, and **ask the machine where they come
from**. That is the only honest way to compare two distributions.

### Who publishes the fixes, and who sells the support

The announced duration often hides a change of hands, and the guide documents
it for the three distributions.

At **Debian**, years 4 and 5 are not carried by the Debian security team but by
the **Debian LTS Team**, funded by corporate sponsorship organised by Freexian:
Debian's independence does not mechanically extend to the end of its cycle. At
**Ubuntu**, the most widespread misconception is to believe that ESM takes over
after five years: that is true for `main` (`esm-infra`), false for `universe`,
covered by `esm-apps` **from the first year**. At **AlmaLinux**, the ten years
are real but come with an obligation in return: there is **no free EUS**, a
minor version dies when the next one is released, so staying covered means
**following the branch** and not freezing a state.

The next criterion follows from that and can be stated in one sentence: is
there anyone to call, and at what price?

- **RHEL** is paid for, in the form of a subscription with support: what you pay
  for is not the software but the support, the certifications and the
  compliance.
- **AlmaLinux** is the opposite: the foundation **sells nothing**, there is no
  subscription to activate nor subscription agent to install. Commercial support
  does exist, but it is sold by a third party (TuxCare, at CloudLinux, which
  funds the foundation).
- **Ubuntu** holds the middle position: Ubuntu Pro is free up to 5 machines for
  personal use (50 for official members of the community), paid beyond that,
  starting at 500 dollars per machine per year at the public price recorded by
  the guide in July 2026.
- **Debian** has no vendor: beyond LTS, ELTS is a commercial service from
  Freexian.

These amounts and these dates are the most perishable facts in this course.
Check them again at the source before making a binding decision: the guide's
comparison gives the official pages to consult.

### The package ecosystem: the right question is not "how many"

The third criterion is often phrased in terms of volume. Volume, however,
settles nothing. On the measurement workstation, the archive announces more
than 82,000 binary packages, all components taken together:

```bash
apt-cache stats
```

```text
Total package names: 162684 (4 555 k)
[...]
  Normal packages: 82982
[...]
```

No serious distribution is short of packages. What makes the difference is
**which ones exist and under what name**, and the AlmaLinux 10 guide gives
three examples that cost dearly when you discover them in production:

- **`redis` no longer exists** in the EL10 generation. The replacement is
  `valkey`. An automation role that installs `redis` does not degrade: it
  breaks, on a package-not-found message.
- **Docker is outside the distribution**: you have to go through the vendor's
  repository, or use Podman, which is present and covered.
- **`fail2ban` and `certbot` come from EPEL**, a Fedora community repository
  with no service commitment whatsoever.

The symmetry is instructive: both families have a coverage gap, it is simply
not in the same place, in `universe` at Ubuntu, on the AppStream/EPEL border at
AlmaLinux. So the question is not "who covers the most" but **"which gap can I
live with"**, and that depends entirely on what you put on the machine.

### Compatibility with third-party software: a contractual problem

The fourth criterion is the one technical comparisons miss most often, and yet
it is the real reason why companies pay for RHEL.

A business application, an ERP, a proprietary database are **certified** for a
specific distribution, almost always RHEL, sometimes Ubuntu, rarely anything
else. The AlmaLinux 10 guide states the case plainly: software certified for
RHEL **will work** on AlmaLinux, since the binary interface is compatible, but
**the vendor will not support it** as long as the certification does not exist.
If you open a ticket, the first question will be about your distribution and the
answer will be to reproduce the problem on RHEL. The cost of that choice is
therefore **not technical, it is contractual**: nil for a web server or an
in-house infrastructure, decisive for a machine carrying a critical business
application under contract.

### The team's skills: four gaps you pay for in training

The fifth criterion is the most underestimated: what your team already knows
how to do. The two families made four different technical choices, and each is
paid for in learning time. Each line points to the lab that teaches it.

| Area | Red Hat family | Debian family | Labs |
|---|---|---|---|
| Packages | `dnf` / `rpm` | `apt` / `dpkg` | `l2-package-management`, `lfcs-package-apt` |
| Mandatory access control | SELinux | AppArmor | `l4-selinux-context-fix`, `lfcs-apparmor` |
| Firewall | firewalld | ufw | `l4-firewall-persist`, `lfcs-firewall-ufw` |
| Network | NetworkManager | netplan | `l4-network-static-persist`, `lfcs-netplan-static` |

These gaps are not cosmetic. One example per line is enough to show it.

**Packages: two philosophies of removal.** The lab `l2-package-management`
measured that `dnf remove` **cleans up dependencies that have become orphans**,
because `clean_requirements_on_remove=True` is active by default in
`/etc/dnf/dnf.conf`. The lab `lfcs-package-apt` measured the opposite: `apt
remove` leaves the orphan in place, merely reports
`Use 'sudo apt autoremove' to remove it.` and waits for a second command. The
same intention from the administrator, two different states of the system at
the end.

**Mandatory access control: two worlds.** On this workstation, the question is
settled in two commands:

```bash
aa-status --enabled ; echo "AppArmor actif : $?"
ls /sys/fs/selinux
```

```text
AppArmor actif : 0
ls: cannot access '/sys/fs/selinux': No such file or directory
```

A zero exit code for AppArmor, and no trace of SELinux. On an AlmaLinux, the
lab `l4-selinux-context-fix` records exactly the opposite: `getenforce` answers
`Enforcing`. That is not a preference, it is a complete change of scenery, with
its own commands (`semanage`, `restorecon`, `ls -Z`) and its own failures.

**Firewall and network: the tools are not even installed.** Still on this
workstation:

```bash
command -v nmcli firewall-cmd ufw netplan nft
```

```text
/usr/sbin/netplan
/usr/sbin/nft
```

Three of the five binaries looked for do not exist here. A procedure written
for one of the families does not run on the other: it fails at the first
command, on a "command not found". That is the real cost of changing family,
far more than the syntax.

> Worth noting, because it is counter-intuitive: the guide records that **none
> of the cloud images measured, Debian as well as AlmaLinux, has a firewall
> installed**. The "firewalld active by default" attributed to the Red Hat
> family is true for an installation from the ISO, false for a cloud image.
> Filtering is your responsibility in every case.

### The Red Hat landscape since 2023, and what it changes for the RHCSA

This is the question every beginner asks when faced with the names in
circulation. Here is what the guide establishes, and nothing more.

**AlmaLinux and Rocky Linux are free rebuilds of RHEL**, usable to train on an
environment identical to RHEL at no cost. They are the two distributions the
guide recommends for preparing the RHCSA, while recalling that **the exam
itself is taken on RHEL**.

**Since July 2023, they no longer aim at the same target.** AlmaLinux abandoned
"1:1, bug for bug" compatibility in favour of **ABI compatibility**: a binary
compiled for RHEL works on AlmaLinux. Rocky Linux, for its part, **still claims
bug for bug**. The guide insists on two points of caution:

- Do not write "AlmaLinux is no longer RHEL-compatible": that is false, and
  three years on, there is no documented case of software broken by that
  difference.
- Do not write "Red Hat violates the GPL" either: neither the Software Freedom
  Conservancy nor the Free Software Foundation says so, and only a court could
  settle it.

**The most concrete consequence is hardware.** RHEL 10 and its rebuilds require
an `x86-64-v3` processor (roughly an Intel Haswell from 2013 or newer).
AlmaLinux provides **in addition** an `x86-64-v2` variant, which Rocky does
not. On a hypervisor exposing a generic CPU (`kvm64` by default on Proxmox),
the virtual machine **does not boot**, on a misleading `Fatal glibc error`.
That is the first trap to know about if you build your own training laboratory.

**For the RHCSA, in practice**, this landscape changes almost nothing: the
configuration files, the `systemd`, `dnf` and `firewalld` commands are those of
RHEL, and that is what the exam checks. The choice between AlmaLinux and Rocky
comes down to operational details, the hardware available first of all.

> **What this course will not assert.** You will also come across the name
> **CentOS Stream**. This site's corpus places it in the Red Hat ecosystem, on
> the same footing as RHEL, Rocky and AlmaLinux (same tools, `dnf` and firewalld
> by default), but no guide gives its life cycle and **none proposes it for
> preparing the RHCSA**: the two distributions named for that are AlmaLinux and
> Rocky. Do you want to know precisely what CentOS Stream is and how it stands
> relative to RHEL? Go and check with the project itself. This course would
> rather say nothing than pass on an approximation to you, and that is exactly
> the reflex this lab wants to give you.

### Summary: start from your situation, not from supposed merits

The guide's comparison enters by situation rather than by distribution. That is
the right way to decide, because it makes visible **what you accept in
exchange**.

| Your situation | What the guide proposes | What you accept in exchange |
|---|---|---|
| A self-hosted stack: containers, cache, reverse proxy, `fail2ban`, `certbot` | Debian 13 | a 5-year cycle, so a migration to prepare earlier |
| A long-lived, stable estate, with no subscription budget | AlmaLinux 10 | `fail2ban` and `certbot` out of scope (EPEL), and an `x86-64-v3` CPU required |
| Public cloud, official images everywhere | Ubuntu 26.04 LTS | `universe` not covered without Ubuntu Pro |
| A business application certified for RHEL | RHEL | a subscription, in exchange for contractual support |
| Preparing the RHCSA | AlmaLinux or Rocky Linux | nothing: the environment is the one of the exam |

One last piece of advice from the guide, for anyone with no constraints: start
with Debian or Ubuntu Server LTS, it is the simplest path, and you will move to
a Red Hat distribution later without difficulty. The concepts are the same;
only a few administration commands change, and you have just seen which ones.
One rule holds for every family, by the way: **always choose a long-term
support version**. Ubuntu also publishes interim releases (25.04, 25.10) with
nine months of support, which makes no sense for a server.

# Lab — Identify your Linux machine

## Reminder

[**Install Linux in a virtual machine**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/)

To learn Linux administration, you need a system to practise on. The guide
settles on the **virtual machine** installed on your workstation: you get a
complete, isolated server that you can break and recreate at will without
touching your main system. It walks through choosing the virtualisation
software, downloading the ISO, creating the machine and the minimal
installation. This lab adds what reading alone does not tell you: why the three
other ways of having a Linux at hand are not equivalent for this job, how to
check that hardware virtualisation is really there before losing an hour, and
what makes a study machine useful or painful to live with.

## The course

The examples below do not deal with the challenge: they look at the workstation
that hosts the machines of this training, not at yours. None of them writes
anything.

Every output reproduced here was taken on the host workstation of the training
fleet, an **Ubuntu 24.04.2 LTS**, with **read-only** commands and **without a
single `sudo`**: the account used belongs to the `kvm` and `libvirt` groups
(checked with `id -nG`), which is enough to query the hypervisor.

### Four ways of having a Linux, and what they let you administer

The fundamentals guide says it in one line: you need "a Linux terminal (VM, WSL,
cloud server…)". Those routes all exist, but they do not put the same machine
into your hands.

| Route | What you get | What is missing to learn administration |
|---|---|---|
| **Local VM** (VirtualBox, VMware, KVM/libvirt) | a complete operating system, with its own kernel | nothing: this is the guide's choice |
| **Container** (Docker, Podman) | an application and its dependencies, on the host kernel | the kernel is not yours, the isolation is weaker |
| **WSL2** (Windows) | a Linux kernel compiled by Microsoft, integrated into Windows | it is neither your kernel nor your machine lifecycle |
| **Remote server** (hosting provider) | a machine reachable over SSH | no console if you cut the network |

The beginner's first reflex is to grab whatever installs fastest. That is often
the container, and that is where the disappointment comes, later.

The guide on virtual machines is clear on this point: **a container is not a
small VM**. A VM carries a complete operating system, kernel included, whereas a
container **shares the host kernel** and carries only the application and its
direct dependencies. Hence the table in the guide:

| Question | VM | Container |
|---|---|---|
| How much does it weigh? | several GB | a few MB |
| Startup time | minutes | seconds |
| Isolation level | strong (separate systems) | medium (shared kernel) |
| Learning and experimenting | **recommended** | at a later stage |

The consequence is direct: since there is **only one kernel**, the host's,
everything that belongs to the kernel is out of the container's reach. Yet
system administration is largely made of that: rebooting and checking that the
configuration survived, partitioning and formatting a disk, setting up a
firewall. Note in passing that containers only run natively on Linux: Docker on
Windows or on macOS relies on a hidden Linux VM.

**WSL2** is a case apart, and a good tool: it is a real Linux kernel, but
compiled by Microsoft, not the one from your distribution. Unlike a classic VM
that reserves CPU and RAM in advance, WSL2 shares the workstation's resources
dynamically, and it is **Windows** that holds the controls of the machine:
`wsl --shutdown` stops everything, `wsl --terminate Ubuntu` stops one
distribution, and a `.wslconfig` file on the Windows side sets the memory and
the number of processors. You administer a Linux, without administering the
machine that carries it.

The **remote server at a hosting provider** asks nothing of your workstation and
is worked on over SSH, exactly as the guide teaches you to work on your VM. The
fundamentals block does not detail it; remember that a network or firewall
mistake leaves you there with no emergency door, whereas the console of a local
VM always stays accessible.

### Hardware virtualisation is checked, not assumed

The KVM installation guide is categorical: without the **Intel VT-x** or
**AMD-V** extensions, your virtual machines run in **pure emulation**, that is
to say very slowly. And the troubleshooting table of the VM installation guide
puts the "VT-x is not available" message down to a single cause:
virtualisation disabled in the workstation's BIOS/UEFI. Four checks, from the
fastest to the most precise.

**1. What the processor announces.**

```console
$ lscpu | grep -i virtu
Address sizes:                           39 bits physical, 48 bits virtual
Virtualization:                          VT-x
```

Only the second line counts: the first only shows up because `-i` matches
"virtual" inside "48 bits virtual". `VT-x` denotes an Intel processor; on AMD,
that line shows `AMD-V`.

**2. The count of cores that carry the extension.**

```console
$ grep -Ec '(vmx|svm)' /proc/cpuinfo
32
```

The guide gives the reading of that number: `0` means no support or support
disabled in the BIOS, any higher value means that virtualisation is active.
`vmx` is the Intel extension, `svm` the AMD one.

**3. The kernel's entry point.**

```console
$ ls -l /dev/kvm
crw-rw---- 1 root kvm 10, 232 juil. 22 20:02 /dev/kvm
```

The file exists: the kernel exposes hardware acceleration. If it is missing, the
KVM guide points to the same cause as above, virtualisation disabled in the
BIOS. Note the owning group `kvm` and the `rw-` rights granted to it: this is
what lets an account that is a member of that group use it without becoming
administrator.

**4. The modules actually loaded.**

```console
$ lsmod | grep kvm
kvm_intel             487424  41
kvm                  1404928  16 kvm_intel
irqbypass              12288  1 kvm
```

The specific module confirms the vendor: `kvm_intel` goes with `vmx`, `kvm_amd`
would go with `svm`. The `41` on the first line is the number of users of the
module: on this workstation, virtual machines are using it right now.

These four checks also apply to **WSL2**, which relies on Hyper-V: its guide
lists "Virtualization disabled" among the common errors, with the same fix in
the BIOS.

### Sizing a study machine

The guide gives the format that is enough to learn, and the prerequisites on the
workstation side: at least **4 GB of RAM** and **20 GB of disk space**
available.

| Resource | Value recommended by the guide |
|---|---|
| RAM | 2 GB |
| CPU | 2 vCPU |
| Disk | 20 GB, dynamically allocated |
| Network | NAT |

This is not a theoretical ideal. The fleet of this training is declared in the
`meta.yml` file of the repository, and it lives below those values:

| Machine | RAM | vCPU | Disk |
|---|---|---|---|
| main RHCSA target | 2048 MB | 2 | 20 GB (+ 10 GB) |
| second RHCSA target | 1536 MB | 1 | 15 GB |
| LFCS target | 1536 MB | 1 | 15 GB |

Result on the host workstation, at the time of the capture:

```console
$ virsh list
 Id   Name                   State
--------------------------------------
 14   web1.lab               running
 15   web2.lab               running
 16   control-node.lab       running
 [...]
 21   alma-rhcsa-2.lab       running
 22   ubuntu-lfcs-1.lab      running
 25   alma-rhcsa-1.lab       running
```

Several complete systems run at the same time, precisely because none of them
exceeds 2 GB. A server with no graphical interface makes do with very little:
this is why the guide insists on the **minimal** installation, with no desktop
and no web server.

Two sharing rules, taken from the guide on virtual machines: **the CPU is lent**,
the hypervisor handing out compute time in turn, so that promising more vCPUs
than there are real cores works as long as the machines are not all working flat
out at the same time; **the memory, on the other hand, is reserved**, and giving
4 GB to a machine takes 4 GB away from the workstation even if it only uses
500 MB. So it is memory that limits the number of machines you will be able to
start.

### Fixed-size or dynamically allocated disk

The disk of a virtual machine is a **file** on the host workstation. Two ways of
filling it, independent of the file format (`.vdi` for VirtualBox, `.qcow2` for
KVM, `.vmdk` for VMware):

| Criterion | Dynamic allocation (thin) | Fixed size (thick) |
|---|---|---|
| Space consumed | what is actually written | everything, from creation onwards |
| Creation | fast | slower, the space is reserved |
| Performance | variable, space is allocated on the fly | constant |
| Risk | workstation saturation if you do not watch it | space tied up for nothing |
| Use case chosen by the guide | labs, tests | critical production, databases |

Concretely, a 100 GB disk declared as dynamic starts at a few MB; after
installing a system that takes up 8 GB, the file is about 8 GB, while the
machine still sees 100 GB. Hence the guide's **20 GB dynamically allocated**:
some margin, without paying for the space right away. The downside is real,
several machines growing at the same time can fill the workstation's disk, and
it is the workstation that goes down, not only the offending machine.

### The snapshot, the safety net of the learner

This is what changes everything when you start, because learning consists
precisely in breaking things. The guide distinguishes three moves that are often
confused:

| Move | What it is | Independent of the original disk? |
|---|---|---|
| **Snapshot** | a photograph of the state at a given instant | no |
| **Clone** | a complete copy of the machine | yes |
| **Backup** | the export of the configuration and of the disk | yes |

It is almost instantaneous to create and costs little space: with a QCOW2 disk,
the original disk is frozen read-only and subsequent writes go into a difference
file, which reverting consists in throwing away. The counterpart holds in two
points that the guide does not hide: the snapshot **depends** on the original
disk, and stacking them degrades performance, since each read has to travel
through the chain.

The golden rule is remembered in one sentence: **a snapshot protects against
logical mistakes, not against hardware failures**. It lives in the same storage
as the machine; if the workstation's disk dies, both disappear together. For a
real backup, you must export the machine elsewhere.

The commands, depending on the tool:

```bash
# VirtualBox
VBoxManage snapshot "debian-lab" take "avant-maj" --description "Système propre post-install"
VBoxManage snapshot "debian-lab" list
VBoxManage snapshot "debian-lab" restore "avant-maj"
```

```bash
# KVM / libvirt
virsh snapshot-create-as ma-vm --name "avant-upgrade" --description "État stable"
virsh snapshot-list ma-vm
virsh snapshot-revert ma-vm --snapshotname avant-upgrade
```

Get into the habit of naming the snapshot after what it precedes
(`avant-upgrade-noyau`, `2026-01-31-stable`) and of taking it **before** the
risky operation, never after. Reverting stops the machine if it is running,
restores the disk and loses everything done since: that is exactly the intended
effect.

### Troubleshooting

| Symptom | Likely cause | Check or fix |
|---|---|---|
| "VT-x is not available" when starting the VM | virtualisation disabled in the BIOS/UEFI | enable Intel VT-x or AMD-V, then `grep -Ec '(vmx\|svm)' /proc/cpuinfo` must be greater than 0 |
| the VM starts but everything is abnormally slow | no hardware acceleration, the system is emulated | `ls -l /dev/kvm` and `lsmod \| grep kvm` |
| the VM does not boot on the ISO | wrong boot order | put the CD/DVD drive first |
| black screen after the final reboot | the ISO is still mounted | remove the media from the virtual drive and reboot |
| no network after the installation | interface not configured | `ip link` must show the interface UP, then restart the DHCP |
| `ping` works but the package update fails | no DNS resolution | check `/etc/resolv.conf` |
| cannot reach the VM over SSH from the workstation, in NAT mode | the VM is not exposed | add a port forwarding rule, then `ssh -p 2222 user@127.0.0.1` |
| under Windows, "Virtualization disabled" when installing WSL2 | same cause as the first line | enable VT-x/AMD-V in the BIOS |
| the workstation saturates while the VMs look small | dynamically allocated disks that have grown | watch the space actually consumed on the host |

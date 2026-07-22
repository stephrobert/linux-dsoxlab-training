# Lab — tuned performance profile

## Reminder

[**tuned on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/)

`tuned` applies a named bundle of kernel/sysfs tunings. `tuned-adm list` shows
available profiles, `tuned-adm active` the current one, `tuned-adm profile
<name>` switches. The active choice is saved in `/etc/tuned/active_profile`, so it
persists. The `tuned` service must run.

## The course

The examples below switch between `balanced`, `powersave` and a home-made
profile named `atelier-demo`: the challenge will ask you for another profile,
for another use. The goal is to learn the method and to know how to prove that a
profile is really in force, not to copy a line. Every output comes from an
AlmaLinux 10 VM with `tuned-2.27.0`.

### Where the profiles live, and which one is active

A profile is a directory containing a `tuned.conf` file. Two locations, and the
precedence rule that goes with them:

| Location | Contents |
|---|---|
| `/usr/lib/tuned/profiles/<name>/tuned.conf` | the profiles shipped by the distribution, not to be modified |
| `/etc/tuned/profiles/<name>/tuned.conf` | your own profiles |

A local profile with the same name as a system profile **replaces** it. Checked:
by dropping a `/etc/tuned/profiles/powersave/tuned.conf` with a mere
`summary=Version locale de powersave`, that is the description `tuned-adm list`
shows, and it goes back to the system one as soon as the local directory is
removed.

The current state is read in three places, and you have to know all three
because they do not say the same thing:

```bash
tuned-adm active                  # what the daemon is applying right now
cat /etc/tuned/active_profile     # what will be reapplied at the next boot
cat /etc/tuned/profile_mode       # auto (recommended) or manual (chosen)
```

On the demonstration VM, before any handling:

```text
Current active profile: virtual-guest
virtual-guest
auto
```

`auto` means nobody has chosen: `tuned` asked `tuned-adm recommend` for its
opinion, which inspects the role of the machine and answers `virtual-guest`
here. As soon as you run a `tuned-adm profile <name>`, the mode switches to
`manual` and the recommendation is no longer consulted.

```bash
tuned-adm list
```

```text
Available profiles:
- balanced                    - General non-specialized tuned profile
- balanced-battery            - Balanced profile biased towards power savings changes for battery
- desktop                     - Optimize for the desktop use-case
- hpc-compute                 - Optimize for HPC compute workloads
- latency-performance         - Optimize for deterministic performance at the cost of increased power consumption
- network-latency             - ... focused on low latency network performance
- powersave                   - Optimize for low power consumption
[...]
Current active profile: virtual-guest
```

The choice is made on the **use** of the machine: `latency-performance` or
`network-latency` for a workload sensitive to response time, `powersave` on
battery, `virtual-guest` in a VM, `balanced` when in doubt. The companion guide
gives the full table. A bad choice breaks nothing: at worst the machine is
sub-optimal, and a second `tuned-adm profile` fixes it.

### What a profile really tunes: plugins, not a sysctl file

Opening a `tuned.conf` dispels the idea that a profile is just a list of
`sysctl`. Each section between brackets is a **plugin**:

```bash
sed -n '1,20p' /usr/lib/tuned/profiles/balanced/tuned.conf
```

```text
[main]
summary=General non-specialized tuned profile

[modules]
cpufreq_conservative=+r

[cpu]
governor=schedutil|ondemand|powersave
energy_perf_bias=normal
boost=1

[acpi]
platform_profile=balanced
[...]
[scsi_host]
alpm=med_power_with_dipm
```

`[cpu]` drives the frequency governor, `[modules]` loads or unloads kernel
modules, `[scsi_host]` writes into `/sys`, `[vm]` and `[sysctl]` set kernel
parameters. This is why a profile can partially fail in a VM: the hypervisor
does not expose the hardware that some plugins want to drive.

The `include=` keyword lets you **derive** an existing profile rather than copy
it:

```bash
grep -rn '^include' /usr/lib/tuned/profiles/*/tuned.conf
```

```text
/usr/lib/tuned/profiles/balanced-battery/tuned.conf:7:include=balanced
/usr/lib/tuned/profiles/desktop/tuned.conf:7:include=balanced
/usr/lib/tuned/profiles/hpc-compute/tuned.conf:8:include=latency-performance
/usr/lib/tuned/profiles/network-latency/tuned.conf:7:include=latency-performance
[...]
```

Almost all the shipped profiles are derivatives: three or four base profiles,
and variants that add their own touch.

### Writing your own profile

The real need is rarely "one of the fifteen profiles shipped": it is "this one,
plus two settings of my own". You derive, you do not copy.

```bash
sudo mkdir -p /etc/tuned/profiles/atelier-demo
sudo tee /etc/tuned/profiles/atelier-demo/tuned.conf <<'EOF'
[main]
summary=Profil de demonstration derive de balanced
include=balanced

[sysctl]
vm.swappiness = 45
net.core.somaxconn = 2048
EOF
```

It appears in the list immediately, without restarting the service:

```text
- atelier-demo                - Profil de demonstration derive de balanced
```

You apply it, and you measure before/after:

```bash
sysctl -n vm.swappiness net.core.somaxconn     # 30 and 4096
sudo tuned-adm profile atelier-demo
sysctl -n vm.swappiness net.core.somaxconn     # 45 and 2048
```

`tuned-adm profile_info` confirms along the way that the `summary` read is
indeed the one from the local file.

### Checking with `tuned-adm verify`, and reading the real log

`tuned-adm verify` reads the real state of the system back and compares it to
the settings expected by the active profile. This is the command that answers
"is my profile still applied?". Let us simulate a drift:

```bash
sudo sysctl -w vm.swappiness=90
sudo tuned-adm verify
```

```text
Verification failed, current system settings differ from the preset profile.
You can mostly fix this by restarting the TuneD daemon, e.g.:
  systemctl restart tuned
```

The message does not say **what** has drifted. The detail is in
`/var/log/tuned/tuned.log`, and nowhere else:

```text
ERROR  tuned.plugins.base: verify: failed: 'vm.swappiness' = '90', expected '45'
INFO   tuned.plugins.base: verify: passed: 'net.core.somaxconn' = '2048'
```

A `sudo systemctl restart tuned` reapplies the profile and `vm.swappiness` goes
back to 45.

On this VM, `verify` fails **even without a drift**, with these lines:

```text
ERROR  verify: failed: 'module 'cpufreq_conservative' is not loaded'
ERROR  verify: failed: device host0: 'alpm' = 'max_performance', expected 'med_power_with_dipm'
ERROR  verify: failed: device cpu0: 'boost' = 'None', expected '1'
```

None of those three lines comes from the `tuned.conf` written above: they come
from `balanced`, which the profile inherits from. This is concrete proof that
`include=` works. And it is also the "normal" failure in a virtual machine
reported by the guide: the `cpufreq_conservative` module is built into the
kernel (`modprobe: FATAL: Module cpufreq_conservative is builtin`), and virtual
disks refuse power management (`Errno 95 Operation not supported`). On physical
hardware, `verify` must pass.

> A trap to know about: `journalctl -u tuned` is useless for diagnosing a
> profile. During a full profile change, it only showed the five
> `Starting`/`Started` lines from systemd. All the useful detail (plugin by
> plugin, value by value) goes to `/var/log/tuned/tuned.log`.

### The trap that costs hours: tuned and `/etc/sysctl.d/`

On this VM, `vm.swappiness` is 30 although the kernel default is 60, and
**no** file declares it:

```bash
grep -rn swappiness /etc/sysctl.conf /etc/sysctl.d/ /usr/lib/sysctl.d/
# (no match)
grep -n swappiness /usr/lib/tuned/profiles/virtual-guest/tuned.conf
# 23:vm.swappiness = 30
```

The culprit is therefore the active profile. First habit to acquire: **before
looking for a phantom `sysctl` file, look at the tuned profile**.

Who wins when both declare the same parameter? The service starts **after**
`systemd-sysctl`:

```bash
systemctl show tuned.service -p After --value | tr ' ' '\n' | grep sysctl
# systemd-sysctl.service
```

You could conclude that tuned overrides the administrator. The machine says the
opposite. By dropping a competing file:

```bash
echo 'vm.swappiness = 60' | sudo tee /etc/sysctl.d/99-atelier.conf
sudo systemctl restart tuned
sysctl -n vm.swappiness       # 60
```

And after a full **reboot**, still 60. The tuned log explains why:

```text
INFO  tuned.plugins.plugin_sysctl: reapplying system sysctl
INFO  tuned.plugins.plugin_sysctl: Overriding sysctl parameter 'vm.swappiness' from '30' to '60'
```

This is the `reapply_sysctl = 1` option of `/etc/tuned/tuned-main.conf`, active
by default: after applying its profile, tuned **reads** `/etc/sysctl.d/` again
and lets it have the last word. So remember the real order:

1. the tuned profile beats the kernel default;
2. a file in `/etc/sysctl.d/` beats the tuned profile.

Practical consequence: after such a battle, `tuned-adm verify` fails, and
legitimately so. It reports `'vm.swappiness' = '60', expected '30'`, in other
words "the system no longer matches its profile". This is not a bug, it is a
deliberate arbitration.

### What rolls back, and what stays

Two mechanisms coexist, and they do not undo themselves the same way.

`tuned` **restores** what it changed. When leaving a profile, it puts back the
values it had recorded before applying it:

```bash
sudo tuned-adm profile atelier-demo     # swappiness 45, somaxconn 2048
sudo tuned-adm profile balanced         # swappiness 60, somaxconn 4096
```

`tuned-adm off` does the same, more radically:

```bash
sudo tuned-adm off
tuned-adm active
```

```text
No current active profile.
```

Measured before and after, on the `virtual-guest` profile: `vm.swappiness` goes
from 30 to 60 and `vm.dirty_ratio` from 30 to 20, that is the kernel defaults.
The log confirms it (`terminating TuneD, rolling back all changes`). Two side
effects to know about: `/etc/tuned/active_profile` becomes **empty**, and
`/etc/tuned/profile_mode` switches to `manual`. So the `off` is persistent too.
To go back to the automatic recommendation:

```bash
sudo tuned-adm auto_profile
```

`/etc/sysctl.d/`, on the other hand, restores **nothing**. Removing the file
dropped above leaves the value in place, and even a `sysctl --system` does not
bring it back:

```bash
sudo rm -f /etc/sysctl.d/99-atelier.conf
sysctl -n vm.swappiness           # 60, still
sudo sysctl --system >/dev/null
sysctl -n vm.swappiness           # 60, again
sudo systemctl restart tuned
sysctl -n vm.swappiness           # 30: the profile takes over again
```

A `sysctl` value lives in memory until the reboot: removing the file removes the
instruction, not its effect. Here it is tuned that repairs, because its profile
declares the parameter explicitly. Without tuned, you would have had to set it
back by hand with `sysctl -w`.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Cannot talk to TuneD daemon via DBus. Is TuneD daemon running?` | the service is stopped: `sudo systemctl enable --now tuned` |
| `It seems that tuned daemon is not running, preset profile is not activated` | same; the `Preset profile:` line that follows shows the profile that will be applied at boot |
| `Unable to switch profile: Requested profile 'x' doesn't exist.` | typo; the previous profile stays active, nothing is broken |
| `Verification failed, current system settings differ...` | read `/var/log/tuned/tuned.log`: the `verify: failed:` line names the parameter |
| `verify` fails on `alpm`, `boost` or a kernel module | normal in a VM: the hardware cannot be driven, `systemctl restart tuned` reapplies what can be |
| A parameter does not take the value from the profile | a file in `/etc/sysctl.d/` declares it too and wins (`reapply_sysctl`) |
| A parameter is set although no file declares it | it is the tuned profile: `grep -n <param> /usr/lib/tuned/profiles/<profile>/tuned.conf` |
| The profile is no longer the right one after a reboot | check `/etc/tuned/active_profile` and `/etc/tuned/profile_mode`: in `auto`, it is `tuned-adm recommend` that decides |
| `journalctl -u tuned` shows nothing useful | that is expected: the detail is in `/var/log/tuned/tuned.log` |

To undo everything and start again from the initial state:

```bash
sudo rm -rf /etc/tuned/profiles/atelier-demo
sudo rm -f /etc/sysctl.d/99-atelier.conf
sudo tuned-adm auto_profile
```

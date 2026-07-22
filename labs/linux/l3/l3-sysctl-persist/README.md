# Lab — persistent kernel hardening with sysctl

## Reminder

[**sysctl hardening on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/)

`sysctl -w key=value` changes a kernel parameter now (lost on reboot). A file
in `/etc/sysctl.d/*.conf` (`key = value` per line) makes it persistent;
`sysctl --system` reloads every config file. `sysctl -n <key>` reads the live
value.

## The course

The examples below work on `kernel.pid_max` and `net.core.somaxconn`, two
convenience parameters with no effect on security: the challenge will ask you
for other parameters, with other values. The point is to learn the method and
the traps, not to copy a line.

All the outputs in this course were taken on an AlmaLinux 10.2 VM, kernel
`6.12.0-211.7.3.el10_2.x86_64`, with `sysctl` from `procps-ng 4.0.4`. The
default values vary from one distribution and one kernel to another: always
record what is there before changing it.

### A kernel parameter is a file

`sysctl` does only one thing: read and write the kernel variables exposed under
`/proc/sys/`. The hierarchical name and the file path are the **same address**,
the dots replacing the slashes. The two reads are therefore strictly
equivalent:

```console
$ sysctl -n net.core.somaxconn
4096
$ cat /proc/sys/net/core/somaxconn
4096
```

Writing too, both ways:

```console
$ echo 2048 | sudo tee /proc/sys/net/core/somaxconn
2048
$ sysctl -n net.core.somaxconn
2048
$ sudo sysctl -w net.core.somaxconn=4096
net.core.somaxconn = 4096
```

Prefer `sysctl`: it validates the key and tells you when it does not exist,
where an `echo` into a wrong path simply creates an ordinary file.

```console
$ sudo sysctl -w kernel.parametre_inexistant=1
sysctl: cannot stat /proc/sys/kernel/parametre_inexistant: No such file or directory
$ echo $?
1
```

Remember the search command: this machine exposes 1090 parameters (`sysctl -a |
wc -l`), and you will never know their exact names by heart.

```console
$ sysctl -a --pattern 'vm.swappiness|kernel.pid_max'
kernel.pid_max = 4194304
vm.swappiness = 30
```

### Setting a value: now, or durably

Three actions not to be confused.

| Action | Command | Scope |
|---|---|---|
| Read | `sysctl -n <key>` | not applicable |
| Write live | `sudo sysctl -w <key>=<value>` | **lost on reboot** |
| Make durable | a line in `/etc/sysctl.d/*.conf` | re-read at every boot |
| Apply without reboot | `sudo sysctl --system` | re-reads **all** the files |

The winning pair is therefore always the same: **you write the file**, then
**you apply with `sysctl --system`**. The `-w` alone is for trying a value out,
never for configuring a machine.

The file format is minimal, one assignment per line, spaces around the `=` are
free, `#` comments:

```ini
# /etc/sysctl.d/99-atelier.conf
kernel.pid_max = 65536
```

### The reading order, which decides who wins

`sysctl --system` does not read one directory but four sources, in this order:
`/usr/lib/sysctl.d/` (the files of the system and of the packages),
`/run/sysctl.d/` (the volatile one), `/etc/sysctl.d/` (the administrator), then
`/etc/sysctl.conf` right at the end. It announces each file it applies, which
makes it the best diagnostic tool:

```console
$ sudo sysctl --system
* Applying /etc/sysctl.d/10-atelier.conf ...
* Applying /usr/lib/sysctl.d/10-default-yama-scope.conf ...
* Applying /usr/lib/sysctl.d/10-map-count.conf ...
* Applying /usr/lib/sysctl.d/50-coredump.conf ...
* Applying /usr/lib/sysctl.d/50-default.conf ...
* Applying /usr/lib/sysctl.d/50-libkcapi-optmem_max.conf ...
* Applying /usr/lib/sysctl.d/50-pid-max.conf ...
* Applying /usr/lib/sysctl.d/50-redhat.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
* Applying /etc/sysctl.conf ...
[...]
kernel.pid_max = 131072
[...]
kernel.pid_max = 4194304
```

Read this list carefully: the files **are not grouped by directory**, they are
sorted by **name**, across all directories. And since the last assignment
applied wins, a `10-` from `/etc/` loses against a `50-` from `/usr/lib/`. That
is exactly what the output above shows: our `/etc/sysctl.d/10-atelier.conf`
asked for `131072`, but `/usr/lib/sysctl.d/50-pid-max.conf`, applied after it,
put `4194304` back.

```console
$ sysctl -n kernel.pid_max
4194304
```

Rename the same file to `99-atelier.conf` and it comes last:

```console
$ sudo sysctl --system
[...]
* Applying /usr/lib/sysctl.d/50-pid-max.conf ...
* Applying /usr/lib/sysctl.d/50-redhat.conf ...
* Applying /etc/sysctl.d/99-atelier.conf ...
* Applying /etc/sysctl.d/99-sysctl.conf ...
[...]
kernel.pid_max = 4194304
kernel.pid_max = 65536
$ sysctl -n kernel.pid_max
65536
```

> **The rule worth remembering.** With different names, it is the lexical order
> of the **file name** that decides, not the directory. Hence the `99-`
> convention for an administrator setting: it is read last and overrides
> everything else.

The directory counts in one case only: **with an identical name**, the file in
`/etc/` completely masks the one in `/usr/lib/`, which is not even read any
more.

```console
$ sudo sysctl --system | grep pid-max
* Applying /etc/sysctl.d/50-pid-max.conf ...
```

Do not use that for a setting: it is the mechanism meant to neutralise a file
shipped by a package, not to set a value.

### Proving persistence: the reboot

A sysctl setting is only worth something if it comes back at boot. The
demonstration takes a single experiment: set one value through a file, another
through `-w` alone, and reboot.

```console
$ cat /etc/sysctl.d/99-atelier.conf
kernel.pid_max = 65536
$ sudo sysctl -w net.core.somaxconn=8192
net.core.somaxconn = 8192
$ sysctl kernel.pid_max net.core.somaxconn
kernel.pid_max = 65536
net.core.somaxconn = 8192
$ sudo systemctl reboot
```

After the reboot:

```console
$ sysctl kernel.pid_max net.core.somaxconn
kernel.pid_max = 65536
net.core.somaxconn = 4096
```

The file replayed, the `-w` is gone. It is the `systemd-sysctl` service that
re-reads the same directories very early at boot:

```console
$ journalctl -b -u systemd-sysctl --no-pager | tail -2
systemd[1]: Starting systemd-sysctl.service - Apply Kernel Variables...
systemd[1]: Finished systemd-sysctl.service - Apply Kernel Variables.
```

### The trap: deleting the file restores nothing

This is the mistake that costs the most, because it produces no message at all.
A file in `/etc/sysctl.d/` describes what the kernel must **set** at boot; it
does not describe a state to undo. Once the value is written in memory, it
stays there, and `sysctl --system` has nothing that can cancel it.

```console
$ sysctl -n net.core.somaxconn
1024
$ sudo rm /etc/sysctl.d/99-atelier.conf
$ sudo sysctl --system > /dev/null
$ sysctl -n net.core.somaxconn
1024
```

The original value was `4096`. Two ways to get it back, and only two: reboot,
or set it explicitly again.

```console
$ sudo sysctl -w net.core.somaxconn=4096
net.core.somaxconn = 4096
```

> **Hence the method rule.** Record the original value of every parameter
> **before** changing it (`sysctl -n <key>` into a separate file). Without that
> record, going back means a reboot, which is not always possible in
> production.

A useful nuance, measured on the same machine: the trap only closes if **no
other file** declares the parameter. `kernel.pid_max` is set by
`/usr/lib/sysctl.d/50-pid-max.conf`, so deleting our file is indeed enough to
bring it back to `4194304` at the next `sysctl --system`.
`net.core.somaxconn`, for its part, is declared nowhere: nothing puts it back.
The reflex to settle it:

```console
$ grep -rn somaxconn /etc/sysctl.d/ /usr/lib/sysctl.d/ /etc/sysctl.conf
$ echo $?
1
```

### When a value does not come from sysctl.d

Two behaviours are surprising, better to have seen them once.

**An unknown key passes silently with `--system`.** A file containing a
parameter absent from this kernel produced **no message** here and a `0` return
code, because `sysctl --system` implies the `-e` option (ignore errors). The
same line, re-read file by file, complains:

```console
$ sudo sysctl -p /etc/sysctl.d/98-test.conf
net.core.somaxconn = 8192
sysctl: cannot stat /proc/sys/kernel/parametre_inexistant: No such file or directory
$ echo $?
1
```

So do not count on `sysctl --system` to validate your files: re-read each file
with `sysctl -p <file>` after writing it.

**Another tool may have set the value.** On this VM, `vm.swappiness` is `30`
while no sysctl file mentions it: it is `tuned`, active by default on
AlmaLinux, that imposes it through its profile.

```console
$ sysctl -n vm.swappiness
30
$ grep -rn swappiness /etc/sysctl.d/ /usr/lib/sysctl.d/ /etc/sysctl.conf
$ tuned-adm active
Current active profile: virtual-guest
$ grep -n swappiness /usr/lib/tuned/profiles/virtual-guest/tuned.conf
23:vm.swappiness = 30
```

`tuned` runs **after** `systemd-sysctl` at boot: on the parameters it manages,
it has the last word, even against a `99-` file. So when a setting refuses to
hold, look beyond `/etc/sysctl.d/`.

### Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| The value returns to the old one after a reboot | Set with `-w`, with no file | Write in `/etc/sysctl.d/` then `sysctl --system` |
| The file exists but the value does not apply | A file with a lexically greater name rewrites it | Read the order in the output of `sysctl --system`, rename to `99-` |
| The value stays changed after the file is deleted | Nothing puts the original value back | `sysctl -w <key>=<original value>` or reboot |
| No error, but nothing moves | Misspelled key, ignored by `--system` | Re-read the file with `sysctl -p <file>` |
| `cannot stat /proc/sys/...` | The parameter does not exist on this kernel | Check the name with `sysctl -a --pattern <pattern>` |
| The setting holds at boot then changes | A manager (`tuned`, NetworkManager) comes after | Fix it on the manager side, not by stacking sysctl files |

On the hardening values themselves, their justification and the network
settings that can cut off your access to the machine, the companion guide
linked above is the reference: it details the full CIS- and ANSSI-aligned set.

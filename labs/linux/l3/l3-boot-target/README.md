# Lab — default boot target

## Reminder

[**Boot and reboot on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/)

systemd boots the system into a **target**, that is a set of units to activate.
`systemctl get-default` displays the target used at boot,
`systemctl set-default <target>` changes it persistently (it is a symbolic
link), and `systemctl isolate <target>` switches the current state without
writing anything to disk.

## The course

The commands below were run on a working AlmaLinux 10, and the pasted output is
its own. The supporting example goes the opposite way from the challenge: it
**installs** a graphical default target on a server that does not need one, in
order to see the whole mechanism and prove it with a reboot. It is up to you to
transpose.

### A target is not a runlevel

**Runlevels** come from SysVinit: numeric levels (`0` halt, `1` single user,
`3` multi-user with network, `5` graphical interface, `6` reboot). systemd no
longer uses them, but keeps a compatibility layer, and these two truths live
together on the same machine.

The proof is in the unit directory: the `runlevelN.target` are not units, they
are **links** to the real targets.

```bash
ls -l /usr/lib/systemd/system/runlevel*.target
```

```text
runlevel0.target -> poweroff.target
runlevel1.target -> rescue.target
runlevel2.target -> multi-user.target
runlevel3.target -> multi-user.target
runlevel4.target -> multi-user.target
runlevel5.target -> graphical.target
runlevel6.target -> reboot.target
```

Three SysV levels (`2`, `3`, `4`) land on the same target: the mapping is not
one-to-one, it is **historical**. A runlevel was a number, a target is a unit
name with its dependencies.

The `runlevel` command still answers, and it displays two fields: the
**previous** level then the **current** level, `N` meaning "no previous one
since boot".

```bash
runlevel        # → N 3
who -r          # →          run-level 3  2026-07-22 16:18
```

Do not reason on that figure: it is an approximate translation of the systemd
state, not the source of truth.

### The default target is a symbolic link

This is the point that changes your understanding: the default target is not a
line in a configuration file, it is a link.

```bash
systemctl get-default
ls -l /etc/systemd/system/default.target
```

```text
multi-user.target
lrwxrwxrwx. 1 root root 41 May 26 15:21 /etc/systemd/system/default.target -> /usr/lib/systemd/system/multi-user.target
```

`get-default` does nothing more than read this link: `readlink -f` gives the
same answer. And `set-default` does nothing more than rewrite it, it says so
itself:

```bash
sudo systemctl set-default graphical.target
```

```text
Removed '/etc/systemd/system/default.target'.
Created symlink '/etc/systemd/system/default.target' → '/usr/lib/systemd/system/graphical.target'.
```

The link lives in `/etc/systemd/system/`, so it survives an update of the units
shipped by the packages in `/usr/lib/systemd/system/`. That is also why it is
persistent: it is written on disk, not in memory.

The target aimed at must exist, otherwise the command refuses and touches
nothing:

```bash
sudo systemctl set-default toto.target
# → Failed to set default target: Unit toto.target does not exist
# echo $?  →  1
systemctl get-default          # → graphical.target, unchanged
```

### Switching now, or at the next boot

These are two different gestures, and this is the most frequent confusion:

| Command | Immediate effect | Effect at the next boot |
|---|---|---|
| `systemctl isolate <target>` | yes | none |
| `systemctl set-default <target>` | none | yes |

`isolate` starts the units of the requested target and **stops all those that
are not part of it**. From a machine in text mode, moving to the graphical
target stops nothing (it contains all the rest), and the default link is not
touched:

```bash
systemctl is-active graphical.target    # → inactive
sudo systemctl isolate graphical.target
systemctl is-active graphical.target    # → active
systemctl get-default                   # → multi-user.target, unchanged!
runlevel                                # → 3 5  (we came from 3, we are in 5)
```

The machine then runs in a target **different** from its default target. This
is a perfectly normal and perfectly volatile state: a reboot loses it.

Not every target can be isolated. It takes `AllowIsolate=yes` in the unit,
otherwise systemd refuses:

```bash
sudo systemctl isolate basic.target
# → Failed to start basic.target: Operation refused, unit may not be isolated.
```

> **Be careful on a remote machine.** `isolate` stops the units absent from the
> target aimed at. Switching to a target poorer than the current one can cut
> the network, hence your own SSH session, with no way back. On a machine whose
> console you do not have, only isolate towards a target that contains at least
> everything you depend on.

### Proving the persistence with a reboot

Placing the link proves nothing: only a real boot proves that it is read. After
the `set-default graphical.target` above, reboot then observe:

```bash
sudo systemctl reboot
# ... reconnect ...
systemctl get-default        # → graphical.target
runlevel                     # → N 5   (no previous one: this really is a boot)
who -r                       # →          run-level 5  2026-07-22 17:10
systemctl is-active graphical.target multi-user.target
# → active
# → active
```

Both targets are active because the graphical target **contains** the
multi-user target (see the next subsection). The `N` from `runlevel` confirms
that we come out of a boot and not of an `isolate`.

Two reflexes around a reboot, taken from the guide:

```bash
systemctl list-units --failed    # before: a service already failed will stay so
systemctl is-system-running      # after: must answer "running"
```

On the test machine, these two commands give `0 loaded units listed.` and
`running`: booting into the graphical target broke nothing, even though no
graphical interface is installed.

### A target is a set of units, and that can be read

The active targets can be listed:

```bash
systemctl list-units --type=target
```

```text
UNIT                     LOAD   ACTIVE SUB    DESCRIPTION
basic.target             loaded active active Basic System
[...]
multi-user.target        loaded active active Multi-User System
network-online.target    loaded active active Network is Online
[...]
27 loaded units listed.
```

There are many of them because they nest: `sysinit.target`, then
`basic.target`, then the final target. `list-dependencies` unrolls that tree:

```bash
systemctl list-dependencies multi-user.target
```

```text
multi-user.target
● ├─auditd.service
● ├─chronyd.service
● ├─firewalld.service
● ├─NetworkManager.service
● ├─sshd.service
[...]
● ├─basic.target
● │ ├─paths.target
[...]
```

On this machine the complete tree is 119 lines long. The filled circle marks an
active unit, the empty circle an inactive one.

Two different relations populate that tree, and the distinction is the classic
trick question:

- **`Requires=`**: **strong** dependency. If the required unit fails, the
  target fails with it.
- **`Wants=`**: **soft** dependency. The unit is started if it exists; its
  absence or its failure does not prevent the target from completing.

Let us read these relations on the graphical target:

```bash
systemctl show -p Requires -p Wants -p AllowIsolate graphical.target
```

```text
Requires=multi-user.target
Wants=systemd-update-utmp-runlevel.service display-manager.service
AllowIsolate=yes
```

Everything is there. The graphical target **requires** the multi-user target
(hence the two active at the same time above) and additionally **wants** a
display manager. That is its only real contribution.

Now on this server image, that manager does not exist:

```bash
systemctl status display-manager.service
# → Unit display-manager.service could not be found.
```

Since it is in `Wants=` and not in `Requires=`, the graphical target starts all
the same, displaying nothing: the machine did reboot into `run-level 5` with
zero failed unit. That is why a graphical default target on a server is not a
noisy failure, but a silently useless setting.

### Rescue and emergency: understanding them without triggering them

Two troubleshooting targets exist, and you need to know what separates them:

| Target | What it requires | State obtained |
|---|---|---|
| `rescue.target` | `Requires=rescue.service sysinit.target` | initialisation done, local filesystems mounted, a root shell, neither application services nor network |
| `emergency.target` | `Requires=emergency.service` | nothing but a root shell, the root filesystem mounted read-only |

The difference is one line in their units: `rescue.target` asks for
`sysinit.target`, `emergency.target` asks for nothing. It is the last resort
mode, the one that serves when even the rescue mode no longer starts (a mistake
in `/etc/fstab`, for instance). To repair anything there, you first have to
remount the root filesystem writable:

```bash
mount -o remount,rw /
```

These two targets cannot reasonably be reached remotely, and the reason is
written in their services:

```bash
systemctl cat rescue.service | grep -E 'ExecStart=|StandardInput'
```

```text
ExecStart=-/usr/lib/systemd/systemd-sulogin-shell rescue
StandardInput=tty-force
```

`StandardInput=tty-force`: the rescue shell is **attached to a terminal**.
Neither the network nor `sshd` is part of these two targets, so a
`systemctl isolate rescue.target` launched over SSH cuts the very session that
launched it and hands control back to a console nobody is sitting at.

Hence the access through the boot loader: at the GRUB menu, key `e`, you add at
the end of the `linux` line one of these parameters, then `Ctrl+X` to boot once
with:

```text
systemd.unit=rescue.target
systemd.unit=emergency.target
```

This parameter does not modify the `default.target` link: it is only valid for
that boot. Conversely, a `systemd.unit=` forgotten in the permanent GRUB
configuration makes `get-default` lie at every boot.

> **These two targets were deliberately not executed** while this course was
> being written, neither by `isolate` nor at boot: the test machine is only
> reachable over SSH, and either one would have made it unreachable. What
> precedes comes from reading the units (`systemctl cat`, `systemctl show`),
> not from a real switch. Same rule for you: never set `rescue.target`,
> `emergency.target` or `poweroff.target` as the **default** target on a remote
> machine, you would not see it again.

### Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `set-default` accepted but the boot does not change | `runlevel` was read instead of the link | `systemctl get-default` and `ls -l /etc/systemd/system/default.target` are authoritative |
| `Unit X.target does not exist` | name misspelled, `.target` suffix forgotten | `systemctl list-unit-files --type=target` for the exact name |
| `Operation refused, unit may not be isolated` | the target has no `AllowIsolate=yes` | only isolate towards a target meant for it |
| The SSH session drops after an `isolate` | the target aimed at contains neither network nor `sshd` | only the console lets you come back: to be avoided remotely |
| The target changes at boot without anyone doing anything | a `systemd.unit=` is lying around in the kernel parameters | `cat /proc/cmdline`, then the GRUB configuration |
| `journalctl -b -1` answers "no persistent journal was found" | the journal is not persistent on this image | no trace of the previous boot: fall back on `systemctl list-units --failed` of the current boot |

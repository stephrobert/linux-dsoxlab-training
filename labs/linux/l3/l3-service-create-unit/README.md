# Lab — create a systemd service

## Reminder

[**systemd services on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/)

A `.service` unit in `/etc/systemd/system/` has `[Unit]`, `[Service]`
(`Type=`, `ExecStart=`, `Restart=`) and `[Install]` (`WantedBy=`) sections.
After writing or editing it, run `systemctl daemon-reload`. `enable` links it
into a target (boot persistence); `start` runs it now; `enable --now` does both.

## The course

The examples below set up a service named `horodateur`, built around the
`/usr/local/bin/horodateur.sh` script: the challenge will ask you for another
program, another unit name and other checks. The point is to learn the method
and to know how to debug it, not to copy a line. Every output comes from
AlmaLinux 10, **systemd 257**.

### Writing the unit and loading it

You need two things: a program, and a file that tells systemd how to run it. The
program first, with the **execute bit** (its absence is the number one cause of
failure):

```bash
sudo tee /usr/local/bin/horodateur.sh >/dev/null <<'EOF'
#!/bin/bash
echo "horodateur demarre (PID $$)"
while true; do date +%T > /run/horodateur.tick; sleep 5; done
EOF
sudo chmod 0755 /usr/local/bin/horodateur.sh
```

The unit next, in `/etc/systemd/system/`, the directory reserved for the
administrator. Three blocks, three questions: `[Unit]` describes the service,
`[Service]` says **how to start the process**, `[Install]` **which target to
attach it to** at boot.

```bash
sudo tee /etc/systemd/system/horodateur.service >/dev/null <<'EOF'
[Unit]
Description=Horodateur de demonstration

[Service]
Type=simple
ExecStart=/usr/local/bin/horodateur.sh

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now horodateur.service
```

```text
Created symlink '/etc/systemd/system/multi-user.target.wants/horodateur.service' → '/etc/systemd/system/horodateur.service'.
```

That symbolic link **is** the boot activation: `enable` does nothing but create
it in the `.wants` of the target named by `WantedBy=`. `status` confirms the
real state:

```text
● horodateur.service - Horodateur de demonstration
     Loaded: loaded (/etc/systemd/system/horodateur.service; enabled; preset: disabled)
     Active: active (running) since Wed 2026-07-22 15:30:40 UTC; 2s ago
   Main PID: 1780 (horodateur.sh)
     CGroup: /system.slice/horodateur.service
             ├─1780 /bin/bash /usr/local/bin/horodateur.sh
             └─1782 sleep 5
```

Three lines carry everything: **Loaded** gives the file actually loaded and the
boot activation, **Active** the current state, **CGroup** the attached
processes. `enabled` and `active` are independent: one talks about the next
boot, the other about right now.

### Making it fail, then making it come back

A service that is declared but never made to fail has proven nothing. Kill the
main process and look:

```bash
sudo kill -9 $(systemctl show -p MainPID --value horodateur)
sleep 2 && systemctl is-active horodateur
```

```text
failed
```

```text
× horodateur.service - Horodateur de demonstration
     Active: failed (Result: signal) since Wed 2026-07-22 15:30:49 UTC; 2s ago
    Process: 1780 ExecStart=/usr/local/bin/horodateur.sh (code=killed, signal=KILL)
```

The service went down and stays there: the `Restart=no` default restarts
nothing. `journalctl -u horodateur.service` says the same, with timestamps. So
add the restart policy to the `[Service]` section:

```ini
Restart=on-failure
RestartSec=2s
```

And there, without doing anything else, `systemctl` warns you on **every**
command:

```text
Warning: The unit file, source configuration file or drop-ins of horodateur.service changed on disk. Run 'systemctl daemon-reload' to reload units.
```

This is not a cosmetic detail. As long as the reload has not happened, systemd
works on the version it holds in memory, and it proves it:

```bash
sudo systemctl restart horodateur          # warning, then restart
systemctl show -p Restart --value horodateur
```

```text
no
```

The file says `on-failure`, systemd applies `no`. That is how you lose an hour
editing a file "with no effect". After `sudo systemctl daemon-reload`, the same
command finally answers `on-failure`. Second murder attempt, with the PID read
before and after:

```bash
sudo systemctl daemon-reload && sudo systemctl restart horodateur
systemctl show -p MainPID --value horodateur     # 1940
sudo kill -9 1940
sleep 4 && systemctl is-active horodateur && systemctl show -p MainPID --value horodateur
```

```text
active
1950
```

The PID has changed: systemd restarted the program. The journal tells the
sequence, and `Scheduled restart job` is the line you must learn to recognise:

```text
Jul 22 15:31:02 atelier systemd[1]: horodateur.service: Main process exited, code=killed, status=9/KILL
Jul 22 15:31:02 atelier systemd[1]: horodateur.service: Failed with result 'signal'.
Jul 22 15:31:04 atelier systemd[1]: horodateur.service: Scheduled restart job, restart counter is at 1.
Jul 22 15:31:04 atelier systemd[1]: Started horodateur.service - Horodateur de demonstration.
```

`Restart=on-failure` restarts after a non-zero exit code, a signal or a timeout;
`Restart=always` also restarts after a clean exit, which hides broken
configurations.

### `Type=`: what systemd believes about startup

`Type=` does not change how the program is launched, it changes how systemd
**decides that the service has started**. A bad choice produces wrong
diagnostics.

| Type | What systemd considers | What for |
|------|------------------------|----------|
| `simple` | Started as soon as the fork happens, without waiting for the `exec()` | Historical default |
| `exec` | Started when the `exec()` succeeded | The right default for a foreground binary |
| `forking` | Started when the parent process returned | Traditional daemons, with `PIDFile=` |
| `oneshot` | Started when the command has finished | One-off tasks |
| `notify` | Started when the program calls `sd_notify()` | Applications designed for systemd |

The most common trap: a program that **goes into the background by itself**.
With `Type=simple`, systemd follows the process it started, that process exits
right away, and systemd concludes that the service is over. A two-line script
(`/usr/bin/sleep 600 &` then an `echo`) demonstrates it:

```text
○ demo-detache.service - Programme qui passe en arriere-plan
     Active: inactive (dead)

Jul 22 15:31:25 atelier detache.sh[2083]: fils lance en arriere-plan, PID 2085
Jul 22 15:31:25 atelier systemd[1]: demo-detache.service: Deactivated successfully.
```

Worse than "inactive": the child was killed along with the rest of the cgroup,
`pgrep -a "sleep 600"` returns **nothing**. The same file with `Type=forking`
(followed by a `daemon-reload`) gives the expected result, systemd adopting the
survivor as the main process:

```text
     Active: active (running) since Wed 2026-07-22 15:31:33 UTC; 2s ago
    Process: 2208 ExecStart=/usr/local/bin/detache.sh (code=exited, status=0/SUCCESS)
   Main PID: 2209 (sleep)
```

Second trap, symmetrical: `RemainAfterExit=yes` only makes sense with
`oneshot`. A `Type=oneshot` unit that prepares a directory falls back to
`inactive (dead)` as soon as its work is done, which is correct but unreadable
in a `list-units`. The directive makes it keep the `active (exited)` state:

```text
# Type=oneshot alone:               Active: inactive (dead)
# Type=oneshot + RemainAfterExit=yes:
     Active: active (exited) since Wed 2026-07-22 15:31:42 UTC; 22ms ago
    Process: 2349 ExecStart=/usr/bin/install -d -m 0755 /var/tmp/atelier-demo (code=exited, status=0/SUCCESS)
```

Adding it to a `Type=simple` would make no sense: the process is supposed to
stay alive, there is no "after the exit".

### Where the unit lives: `/etc`, `/usr/lib`, and drop-ins

Two directories hold units, and they do not have the same status:
`/usr/lib/systemd/system/` belongs to the **packages** and gets overwritten on
the first `dnf update`; `/etc/systemd/system/` belongs to the
**administrator** and wins. Two files with the same name, one in each
directory, and `systemctl show -p Description --value demo-prio` settles it:

```text
# file only in /usr/lib/ :   Version fournie par le paquet
# after adding it in /etc/ : Version posee par administrateur
```

Hence the rule: **never edit a file in `/usr/lib`**. Two tools do the work for
you. `systemctl edit --full <unit>` copies the whole unit into
`/etc/systemd/system/` and opens it in an editor. `systemctl edit <unit>`
without `--full` creates a **drop-in**, a fragment that contains only the
directives to change:

```bash
sudo systemctl edit --drop-in=redemarrage.conf horodateur.service
```

```text
Successfully installed edited file '/etc/systemd/system/horodateur.service.d/redemarrage.conf'.
```

The fragment is worth two lines (`[Service]` and `RestartSec=10s`), the rest of
the unit still comes from the original file and will follow its updates.
`systemctl cat` shows the stack file by file, and `status` reports the drop-in:

```text
    Drop-In: /etc/systemd/system/horodateur.service.d
             └─redemarrage.conf
```

`systemctl show -p RestartUSec --value horodateur.service` answers `10s`: the
drop-in did override the `RestartSec=2s` of the main file.

### Causing errors to learn how to read them

Three classic mistakes, and what the machine really does with them. **A relative
`ExecStart`** is refused at load time, before any start. The unit takes the
`Loaded: bad-setting` state and `systemctl start` returns 1:

```text
/etc/systemd/system/demo-fautes.service:6: Neither a valid executable name nor an absolute path: ./horodateur.sh
demo-fautes.service: Unit configuration has fatal error, unit will not be started.
```

A nuance worth knowing: a **plain name with no slash** is accepted.
`ExecStart=horodateur.sh` starts without complaining, because systemd looks for
it in a fixed list of directories (`man systemd.service`: "Searched directories
include `/usr/local/bin/`, `/usr/bin/`"). What is forbidden is a **relative**
path, not a bare name. Write the absolute path anyway: it is unambiguous.

**An unknown directive** prevents nothing. On a typo (`Restrt=on-failure`),
systemd **ignores** the key, the service starts, and the restart policy you
think you set does not exist. The warning goes into the system journal on every
`daemon-reload`, where nobody reads it:

```text
Jul 22 15:31:48 atelier systemd[1]: /etc/systemd/system/demo-fautes.service:7: Unknown key 'Restrt' in section [Service], ignoring.
```

**Without an `[Install]` section**, `systemctl enable` creates **no link** and
still returns the exit code **0**: a script testing `$?` will believe the
activation succeeded. Only the printed explanation gives the problem away.

```text
The unit files have no installation config (WantedBy=, RequiredBy=, UpheldBy=,
Also=, or Alias= settings in the [Install] section, [...])
```

`systemctl is-enabled` then answers `static`, and that is the only check that
counts: never the exit code of `enable`.

These mistakes are caught **before** the first start with
`systemd-analyze verify <file>`, which reads the unit the way systemd would and
goes further than syntax (it checks that the executable of `ExecStart=`
exists):

```text
demo-fautes.service: Command /usr/local/bin/absent.sh is not executable: No such file or directory
rc=1
```

On a healthy unit, it prints nothing and returns 0. Mind the severity levels: an
invalid path and a missing executable give `rc=1`, an unknown key is merely
reported, with `rc=0`.

This last case illustrates the `Type=simple` trap: with an `ExecStart` pointing
at a missing file, `systemctl start` returns **0** while the service dies right
away (`start rc=0`, then `is-active` answers `failed`).

```text
Jul 22 15:32:42 atelier systemd[1]: demo-fautes.service: Main process exited, code=exited, status=203/EXEC
```

**203/EXEC** is the most frequent failure code: binary not found, not
executable, or a typo in the path. Never trust the exit code of `start` with
`Type=simple`: check the state afterwards with
`sleep 3 && systemctl is-active <unit>`.

### Tearing down cleanly, and troubleshooting

Deleting the file is not enough: the activation link and the `failed` state
survive.

```bash
sudo systemctl disable --now horodateur.service
sudo rm -f  /etc/systemd/system/horodateur.service
sudo rm -rf /etc/systemd/system/horodateur.service.d
sudo systemctl daemon-reload && sudo systemctl reset-failed
systemctl list-units --failed
```

`disable` removes the link
(`Removed '/etc/systemd/system/multi-user.target.wants/horodateur.service'.`),
`daemon-reload` makes systemd forget the unit, `reset-failed` clears the failure
counters. The proof is one line long: `0 loaded units listed.`

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Editing the file has no effect | systemd keeps its version in memory | `systemctl daemon-reload`, then `restart` |
| `start` succeeds but the service is dead | `Type=simple` does not check the `exec()` | `sleep 3 && systemctl is-active <unit>`, or `Type=exec` |
| `failed` with `203/EXEC` | Binary missing or not executable | `ls -l` on the `ExecStart=` path, then `chmod +x` |
| `inactive (dead)` right after `start` | The program goes into the background | `Type=forking`, or run the program in the foreground |
| `enable` creates no link | No `[Install]` section | Add `WantedBy=multi-user.target`, `daemon-reload`, enable again |
| `Loaded: bad-setting` | Fatal directive, often a relative `ExecStart` | `systemd-analyze verify <file>` |
| A directive seems ignored | Typo in the key | `journalctl -b \| grep "Unknown key"` |
| The service runs but disappears on reboot | Never enabled | `systemctl enable <unit>` then check `is-enabled` |

The other exit codes (`217/USER`, `200/CHDIR`), hardening with
`systemd-analyze security` and targets are covered in the companion guide linked
at the top of the page.

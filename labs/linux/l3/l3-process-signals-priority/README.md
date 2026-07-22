# Lab — process priority with Nice

## Reminder

[**Processes on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/)

Nice values run from `-20` (highest priority) to `19` (lowest). `nice -n N cmd`
starts a process at a priority, `renice N -p PID` changes the one of a running
process. For a service, `Nice=` in the unit (or a `systemctl edit` drop-in)
makes it durable. Signals — `kill -TERM/-HUP/-9` — control running processes.
`ps -o ni -p <pid>` shows the current nice.

## The course

The examples below work on demonstration processes that you create yourself and
on a service named `atelier-veille`: the challenge will be about another service
and another value. The goal is to learn the method and to know how to check it,
not to copy a line. Every output that follows comes from an AlmaLinux VM with a
**single core**.

### A signal is a message, and the process can answer it

`kill` is badly named: it **sends a signal**, and it is the process that decides
what to do with it. To see that, you need a process that installs handlers
(`trap`) instead of undergoing the default behaviours:

```bash
mkdir -p ~/atelier-signaux
cat > ~/atelier-signaux/veilleur-atelier.sh <<'EOF'
#!/bin/bash
journal=/tmp/veilleur-atelier.log
trap 'echo "$(date +%T) TERM recu : je range et je sors" >> $journal; exit 0' TERM
trap 'echo "$(date +%T) HUP recu : je relis ma configuration" >> $journal' HUP
echo "$(date +%T) demarrage, PID $$" >> $journal
while true; do sleep 1; done
EOF
chmod +x ~/atelier-signaux/veilleur-atelier.sh
```

Start it in the background and keep its PID, which `$!` always gives:

```bash
~/atelier-signaux/veilleur-atelier.sh &
pid=$!
kill -HUP "$pid"; sleep 2; cat /tmp/veilleur-atelier.log
```

```text
15:33:01 demarrage, PID 21717
15:33:03 HUP recu : je relis ma configuration
```

`SIGHUP` did not kill the process: its handler ran and the loop resumed. This is
the mechanism behind "reload the configuration without restarting the service".
`ps -o pid,stat,comm -p "$pid"` confirms it, truncating the name to 15
characters (`veilleur-atelie` is not a typo).

Now for `SIGTERM`, which the script catches to exit cleanly:

```bash
kill -TERM "$pid"; sleep 2; cat /tmp/veilleur-atelier.log
ps -o pid,stat,comm -p "$pid" || echo "(ps ne trouve plus rien)"
```

```text
15:33:03 HUP recu : je relis ma configuration
15:33:05 TERM recu : je range et je sors
    PID STAT COMMAND
(ps ne trouve plus rien)
```

Start the watcher again and send it `SIGKILL` this time: the process
disappears, but the log gains no line.

```text
--- kill -KILL 21759
--- log contents:
15:33:15 demarrage, PID 21759
--- process still there? (gone)
```

That is the fundamental distinction of the subject: with `-TERM` the process
**sees** the signal and can close its files, flush its buffers, remove its lock;
with `-KILL` it is the kernel that removes it, and no `trap` runs. Hence the
rule: `TERM` first, you wait, `KILL` only if nothing moves. `man 7 signal` puts
it this way:

```text
The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored.
```

One last point about signals: **the name is portable, the number is not.**
`kill -l` lists the signals of the machine and translates both ways
(`kill -l TERM` answers `15`, `kill -l 9` answers `KILL`):

```text
 1) SIGHUP	 2) SIGINT	 3) SIGQUIT	 4) SIGILL	 5) SIGTRAP
 6) SIGABRT	 7) SIGBUS	 8) SIGFPE	 9) SIGKILL	10) SIGUSR1
11) SIGSEGV	12) SIGUSR2	13) SIGPIPE	14) SIGALRM	15) SIGTERM
```

These numbers hold **for this architecture**. Excerpt of the table in
`man 7 signal`, whose columns are x86/ARM, Alpha/SPARC, MIPS and PARISC:

```text
SIGKILL          9           9       9       9
SIGUSR1         10          30      16      16
SIGTERM         15          15      15      15
```

`SIGUSR1` is 10 here, 30 on Alpha, 16 on MIPS. So write `kill -HUP` rather than
`kill -1`: the name always designates the same signal.

### The states of a process, and how to make one

`ps` summarises the state in the `STAT` column: `R` running, `S` in an
interruptible sleep, `T` stopped, `Z` zombie, `D` blocked on an uninterruptible
I/O. Two of them are easy to make.

A stopped process, with `SIGSTOP` then `SIGCONT`:

```bash
sleep 120 & p=$!
kill -STOP "$p"; sleep 1; ps -o pid,stat,comm -p "$p"
kill -CONT "$p"; sleep 1; ps -o pid,stat,comm -p "$p"
```

```text
-- after kill -STOP
  22497 T    sleep
-- after kill -CONT
  22497 S    sleep
```

A zombie, by letting a child die that its parent does not reap:

```bash
bash -c 'sleep 1 & exec sleep 60' & z=$!
sleep 3; ps -o pid,ppid,stat,comm --ppid "$z"
```

```text
    PID    PPID STAT COMMAND
  22521   22506 Z    sleep
```

A zombie consumes neither CPU nor memory: all that is left of it is its return
code, which the parent has not read. There is therefore nothing to kill, and
`kill` on a zombie does nothing. You act on the **parent**: `kill -TERM` on PID
22506 makes both disappear, `systemd` adopting then reaping the orphan.

The `D` state cannot be produced cleanly: it takes an I/O that never comes back
(failing disk, unreachable network mount). It is the only state where `kill -9`
itself has no effect, the process not being interruptible while the kernel waits
for the device. A `D` that lasts is a hardware or network symptom, not a process
problem.

### `nice` and `renice`: setting then changing the priority

`nice -n N command` sets the priority at **launch**, `renice -n N -p PID`
changes it **along the way**. An ordinary user can only lower their own, never
raise it back:

```bash
sleep 300 & p=$!
renice -n 12 -p "$p"
renice -n 5 -p "$p"; echo "code retour = $?"
sudo renice -n 5 -p "$p"
```

```text
22089 (process ID) old priority 0, new priority 12
renice: failed to set priority for 22089 (process ID): Permission denied
code retour = 1
22089 (process ID) old priority 12, new priority 5
```

Same logic at launch: `nice -n -5 sleep 2` displays
`nice: cannot set niceness: Permission denied` and starts the command anyway, at
nice 0. The ceiling is the one of `ulimit -e`, which is `0` for an ordinary
account on this machine. The practical consequence: without `sudo`, lowering
your priority is a one-way trip.

There remains one column that puzzles people, `PRI`, displayed next to `NI`:

```bash
for n in 0 5 19; do nice -n $n sleep 60 & done
sudo nice -n -5 sleep 60 &
ps -o pid,ni,pri,stat,comm -C sleep
```

```text
    PID  NI PRI STAT COMMAND
  22601   0  19 S    sleep
  22602   5  14 SN   sleep
  22603  19   0 SN   sleep
  22607  -5  24 S<   sleep
```

In the `ps` display, `PRI` equals `19 - NI`: it rises when `NI` falls. Both say
the same thing in opposite directions, and `NI` is the one you set. Note in
passing the `STAT` flags: `N` for a low priority, `<` for a high one.

### The priority only shows under contention

On an idle machine, nice changes **nothing** visible: there is no queue to
arbitrate. A compute loop on its own, at the lowest possible priority, still
gets the whole processor:

```text
--- alone on the machine, at nice 19, for 5 s:
    PID  NI PRI STAT     TIME COMMAND
  22061  19   0 RN   00:00:04 boucle-atelier.
```

Four seconds of CPU in five seconds of wall time, at nice 19. To observe an
effect, you need more runnable processes than cores. `nproc` gives the number of
cores; here it is `1`, so two loops are enough:

```bash
cat > ~/atelier-signaux/boucle-atelier.sh <<'EOF'
#!/bin/bash
while :; do :; done
EOF
chmod +x ~/atelier-signaux/boucle-atelier.sh
nice -n 0  ~/atelier-signaux/boucle-atelier.sh & a=$!
nice -n 19 ~/atelier-signaux/boucle-atelier.sh & b=$!
sleep 10
ps -o pid,ni,pri,stat,time,comm -p "$a" -p "$b"
kill -TERM "$a" "$b"
```

```text
    PID  NI PRI STAT     TIME COMMAND
  22030   0  19 R    00:00:09 boucle-atelier.
  22031  19   0 RN   00:00:00 boucle-atelier.
```

Nine seconds of CPU against zero displayed: the gap is maximal because the nice
gap is too. The exact value depends on the load at the time of the test, and a
VM shares its processor with its host: redo the measurement rather than quoting
this figure. And **always stop those loops**, they do not stop by themselves; a
few seconds are enough.

### CPU priority and I/O priority are two distinct settings

`nice` arbitrates **processor time**. A backup that saturates the disk without
consuming CPU will therefore not be calmed by a high `nice`. The corresponding
setting for I/O is `ionice`, with its own classes:

```text
 -c, --class <class>    name or number of scheduling class,
                          0: none, 1: realtime, 2: best-effort, 3: idle
 -n, --classdata <num>  priority (0..7) in the specified scheduling class,
                          only for the realtime and best-effort classes
```

The class is indeed recorded by the kernel: after `ionice -c 3 sleep 30 &`, the
command `ionice -p $!` answers `idle`.

On the other hand, **check that it produces an effect on your storage before
counting on it**. On this VM, two concurrent writes of 800 MiB in
`oflag=direct`, one in `best-effort` and the other in `idle`, give very
scattered throughputs; and a control test where **both** are in `best-effort`
produces the same scatter:

```text
essai   A[-c 2 -n 0] :  2.0 GB/s   B[-c 3]      :  1.5 GB/s
temoin  A[-c 2 -n 0] :  876 MB/s   B[-c 2 -n 0] :  2.2 GB/s
```

The control test invalidates the measurement: on a virtio disk served by the
host cache, with the `mq-deadline` scheduler
(`cat /sys/block/vda/queue/scheduler`), nothing here allows us to state that the
`idle` class slows anything down. Remember the CPU / I/O distinction, which is
real, and measure on your own storage before drawing a conclusion from it.

### Making the priority durable for a service

A `renice` on the process of a service does not survive the first restart:

```bash
sudo renice -n 3 -p "$(systemctl show -p MainPID --value atelier-veille)"
sudo systemctl restart atelier-veille
ps -o pid,ni,comm -p "$(systemctl show -p MainPID --value atelier-veille)"
```

```text
22768 (process ID) old priority 15, new priority 3
--- service restart
  22803  15 sleep
```

The durable value is declared in the unit, preferably in a drop-in created by
`systemctl edit <service>`, which leaves the original file intact:

```bash
sudo systemctl edit atelier-veille     # add [Service] then Nice=15
sudo systemctl daemon-reload
sudo systemctl restart atelier-veille
```

`systemctl cat` shows what systemd actually assembled:

```text
# /etc/systemd/system/atelier-veille.service.d/priorite.conf
[Service]
Nice=15
```

Here is the trap, and it is worth seeing in full. After `daemon-reload` alone,
the configuration already announces the new value while the running process has
not moved:

```text
--- daemon-reload alone:
Nice=15                      <- systemctl show -p Nice
  22685   0 sleep            <- ps -o ni on the MainPID
```

You have to **restart** the service for its process to be born with the new
priority:

```text
--- after restart:
MainPID=22768
  22768  15   4 sleep        <- NI=15, PRI=4
```

Hence the two checks to make systematically, one on the configuration, the other
on the actual state:

```bash
systemctl show -p Nice <service>
ps -o ni= -p "$(systemctl show -p MainPID --value <service>)"
```

### Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `systemctl show -p Nice` gives the right value, `ps -o ni` does not | The process is still running with the old priority | `systemctl restart`: the priority is set when the process starts |
| The drop-in is written but `systemctl cat` does not show it | `daemon-reload` not run, or file outside a `<service>.service.d/` directory | `sudo systemctl daemon-reload`, then read `systemctl cat` again |
| `renice: failed to set priority ... Permission denied` | An ordinary account cannot raise a priority back | Go through `sudo`, or restart the process |
| `kill -TERM` has no effect | The process catches `SIGTERM` and takes its time, or it is in state `D` | Wait a few seconds then `kill -KILL`; if the state is `D`, look at the disk or the network mount |
| `MainPID` is `0` | The service is not active | `systemctl status <service>` and read the logs before touching the priority |
| Two processes with different nice values progress the same | No contention: fewer runnable processes than cores | Compare under load, with at least `nproc` + 1 active processes |
| `pkill pattern` kills your own session | The pattern also appears in the command line of the current shell | Target by PID, or choose a pattern that the command itself does not contain |

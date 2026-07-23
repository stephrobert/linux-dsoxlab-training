# Lab — sync the clock with chrony

## Reminder

[**Time synchronization with chrony on the companion guide**](https://blog.stephane-robert.info/docs/services/reseau/chrony/)

`chronyd` is the NTP client on RHEL-family systems. `timedatectl` shows and sets
the timezone (`set-timezone`) and toggles network time (`set-ntp`). A service
must be `enabled` to come back after a reboot: running is not enough.

## The course

The examples below set a workshop machine to the `Indian/Reunion` timezone and
add the `time.google.com` source to it: the challenge will ask you for another
timezone. The goal is to learn the method and to know how to read the output,
not to copy a line. Every output reproduced here was obtained on an AlmaLinux 10
with `chrony 4.8`.

### Two clocks, one display convention

A machine does not carry one clock but two, plus a convention to display them.
`timedatectl` without arguments shows the whole thing at once:

```bash
timedatectl
```

```text
               Local time: Wed 2026-07-22 15:52:47 UTC
           Universal time: Wed 2026-07-22 15:52:47 UTC
                 RTC time: Wed 2026-07-22 15:52:47
                Time zone: UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

- **Local time** and **Universal time** are the same instant, the same system
  clock, displayed twice: once in the configured timezone, once in UTC.
- **RTC time** is the hardware clock, the one on the motherboard, which survives
  a power off and gives the time at boot before the network is available.
- **Time zone** is only a conversion rule for the display.
- **System clock synchronized** is the only field that tells whether the time is
  held by an external source. That is the one you look at first.

The hardware clock can also be read with `hwclock`, but on this KVM virtual
machine the read fails, even though `timedatectl` does display the RTC time and
the write (`sudo hwclock --systohc`) goes through without an error:

```bash
sudo hwclock --show
```

```text
hwclock: select() to /dev/rtc0 to wait for clock tick timed out
```

So do not conclude from a failing `hwclock --show` that the machine has no
hardware clock: rely on the `RTC time` line of `timedatectl`.

### Changing timezone does not change the instant

This is the most frequent confusion. The timezone does not move time, it changes
the way it is written. Proof in three commands, before and after:

```bash
date +"%F %T %Z (%z)"
date -u +"%F %T %Z (%z)"
date +%s
sudo timedatectl set-timezone Indian/Reunion
```

```text
2026-07-22 15:54:08 UTC (+0000)     <- date, before
2026-07-22 15:54:08 UTC (+0000)     <- date -u, before
1784735648                          <- seconds since the epoch, before

2026-07-22 19:54:08 +04 (+0400)     <- date, after
2026-07-22 15:54:08 UTC (+0000)     <- date -u, after
1784735648                          <- seconds since the epoch, after
```

`date` moved by four hours, `date -u` did not move by a single second, and the
epoch is strictly identical. Nothing happened to the clock: only the
`/etc/localtime` link was rewritten.

```bash
ls -l /etc/localtime
```

```text
lrwxrwxrwx. 1 root root 36 Jul 22 19:54 /etc/localtime -> ../usr/share/zoneinfo/Indian/Reunion
```

The timezone catalogue has 598 entries on this machine: filter it instead of
reading it, with `timedatectl list-timezones | grep -i reunion`.

To script a check, `timedatectl show` outputs the same information as
`key=value`, and `-p <key> --value` isolates a single value, with no decoration:

```text
Timezone=Indian/Reunion
LocalRTC=no
CanNTP=yes
NTP=yes
NTPSynchronized=yes
[...]
```

The `LocalRTC` field deserves a word. At `no`, the hardware clock contains UTC;
at `yes`, it contains local time. `timedatectl set-local-rtc 1` switches to that
second mode, and `systemd` itself tries to talk you out of it:

```text
Warning: The system is now being configured to read the RTC time in the local time zone
         This mode cannot be fully supported. It will create various problems
         with time zone changes and daylight saving time adjustments. [...]
         If at all possible, use RTC in UTC
```

On a server, keep `LocalRTC=no`. An RTC in local time forces you to know the
timezone and the daylight saving state to interpret the boot time, which breaks
at the time change and when moving between timezones. You go back with
`sudo timedatectl set-local-rtc 0`.

### Who actually synchronizes, and what `set-ntp` drives

`timedatectl set-ntp` is described everywhere as "the NTP switch", but its
effect depends on what is installed. Look first:

```bash
systemctl list-unit-files --type=service | grep -Ei "chrony|timesync"
```

```text
chrony-wait.service                          disabled        disabled
chronyd-restricted.service                   disabled        disabled
chronyd.service                              enabled         enabled
```

On this AlmaLinux 10, `systemd-timesyncd` does not even exist
(`Unit systemd-timesyncd.service could not be found.`): the switch therefore
acts on `chronyd`. And it acts strongly. Before:

```text
timedatectl show -p NTP --value  -> yes
systemctl is-active chronyd      -> active
systemctl is-enabled chronyd     -> enabled
```

After a `sudo timedatectl set-ntp false`:

```text
timedatectl show -p NTP --value  -> no
systemctl is-active chronyd      -> inactive
systemctl is-enabled chronyd     -> disabled
```

Remember this point: that command does not merely stop the service, it also
**disables** it, so the effect survives the reboot. Another consequence of that
coupling: `timedatectl timesync-status`, often quoted in tutorials, fails on a
machine running chrony (`Failed to query server: The name is not activatable`),
because it queries `timesyncd`. On a chrony system, it is `chronyc` that gives
the state, not `timedatectl`.

### Reading the state with `chronyc`

Two commands are enough. `chronyc sources -v` lists the servers being queried,
with a built-in legend that saves you from memorising the markers:

```bash
chronyc sources -v
```

```text
  .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
 / .- Source state '*' = current best, '+' = combined, '-' = not combined,
| /             'x' = may be in error, '~' = too variable, '?' = unusable.
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* isere.sd.ysun.co              2   6   377    44  +2922us[+3431us] +/-   20ms
^+ 172-234-184-36.ip.linode>     2   6   357   175  -5219us[-6067us] +/-   47ms
^+ ciran28.fr                    3   6   377    46  -2182us[-1673us] +/-   46ms
```

The first character is the mode (`^` = server), the second the state: `*` the
selected source, `+` an acceptable source combined with the previous one, `-` a
source excluded from the computation, `?` an unreachable source. **Reach** is an
octal register of the last eight probes: `377` means eight answers out of eight,
`0` none. **Stratum** gives the distance to the reference clock, **Poll** the
base-2 logarithm of the polling interval (6 means 64 seconds).

`chronyc tracking` answers the other question: by how much is my clock wrong,
and is it drifting?

```bash
chronyc tracking
```

```text
Reference ID    : 17A16885 (isere.sd.ysun.co)
Stratum         : 3
System time     : 0.000176131 seconds slow of NTP time
Last offset     : +0.000508828 seconds
Frequency       : 74.489 ppm slow
Update interval : 65.3 seconds
Leap status     : Normal
```

`System time` is the current offset, here 176 microseconds: that is the figure
that proves a healthy clock. `Frequency` is the intrinsic drift of the crystal,
which chrony measures and compensates continuously, and which it records in its
`driftfile` to find it again at the next boot. `chronyc sourcestats` completes
the picture by giving, source by source, the number of samples kept and the
standard deviation.

### Breaking the clock and watching it get back in line

This is the most telling operation of the lab. As long as network time is
active, the system refuses to let you touch the time: `sudo timedatectl set-time
"2020-01-01 00:00:00"` answers `Failed to set time: Automatic time
synchronization is enabled`.

So you first have to turn synchronization off, then move the clock back. **Stay
on a modest offset**, a few minutes: a jump of several hours or several days
disturbs the logs, triggers scheduled tasks and may expire your SSH session.

```bash
sudo timedatectl set-ntp false
sudo timedatectl set-time "$(date -d '-3 minutes' '+%Y-%m-%d %H:%M:%S')"
timedatectl
```

```text
               Local time: Wed 2026-07-22 19:51:41 +04
[...]
System clock synchronized: no
              NTP service: inactive
```

The clock is three minutes wrong and the system knows it. Turn it back on:

```bash
sudo timedatectl set-ntp true
sleep 8
date "+%F %T"
```

```text
2026-07-22 19:51:47     <- just before
2026-07-22 19:54:56     <- eight seconds later
```

The service journal tells the story of the operation, and shows in passing the
price of a clock jump:

```bash
sudo journalctl -u chronyd --since "-3 min" --no-pager | tail -3
```

```text
Jul 22 19:51:53 atelier chronyd[2076]: Selected source 162.159.200.1 (2.almalinux.pool.ntp.org)
Jul 22 19:51:53 atelier chronyd[2076]: System clock wrong by 180.536616 seconds
Jul 22 19:54:53 atelier chronyd[2076]: System clock was stepped by 180.536616 seconds
```

Look at the timestamps of those three consecutive lines: they go from 19:51 to
19:54. The journal now contains a three-minute hole. This is exactly what you
try to avoid in production.

### Speeding up rather than jumping

Chrony has two ways of correcting a clock. The **slew** slightly changes the
speed of the clock until the offset is caught up: time stays monotonic, no
second is repeated nor skipped. The **step** repositions the clock at once, with
the hole or the overlap we have just seen.

The choice is driven by the `makestep 1.0 3` directive of `/etc/chrony.conf`.
Translation: only allow a jump if the offset exceeds 1 second, and only for the
first 3 updates after the service starts. Beyond that, everything is corrected
by speed adjustment. Let us check with an offset of only 0.5 second, below the
threshold, reading `System time` every five seconds:

```text
T+05s  System time     : 0.481129944 seconds fast of NTP time
T+10s  System time     : 0.000181024 seconds slow of NTP time
T+15s  System time     : 0.000000226 seconds fast of NTP time
```

The offset melts progressively and the journal, this time, contains **no**
`System clock was stepped by` line. The correction was done smoothly.

This is the behaviour to favour on a production server: a database, a cluster or
a distributed file system copes badly with a timestamp going backwards. The jump
remains useful at boot, when the offset is too large to be caught up in a
reasonable time; you can force it by hand with `sudo chronyc makestep`, which
answers `200 OK`.

### Declaring a source, and the traps that cost points

First trap, the path of the file. On this AlmaLinux, the configuration is in
`/etc/chrony.conf`, and the `/etc/chrony/` directory does not exist
(`ls: cannot access '/etc/chrony/': No such file or directory`). The companion
guide quotes `/etc/chrony/chrony.conf`: that is the Debian and Ubuntu location.
Always check which of the two exists before editing.

Second trap, and this is the one that wastes time: **an added source is not
taken into account until the service has restarted**. After adding a line to the
file, `chronyc sources` still counts four sources and does not know the new one:

```bash
echo 'server time.google.com iburst' | sudo tee -a /etc/chrony.conf
chronyc sources | grep -c .    # unchanged
sudo chronyc reload sources    # 200 OK, but no effect here
```

`chronyc reload sources` only re-reads the files of the `sourcedir` directory
(`/run/chrony-dhcp`), not `chrony.conf`. You have to restart with
`sudo systemctl restart chronyd`:

```text
^+ 27.ip-51-68-44.eu             4   6    17     1  -7934us[-8296us] +/-   43ms
^+ time.cloudflare.com           3   6    17     2   -883us[-1245us] +/-   15ms
^* time4.google.com              1   6    17     1   -678us[-1040us] +/-   12ms
```

The new source appears, in stratum 1, and chrony has even selected it (`^*`).
The `iburst` option explains the speed: it sends a burst of requests at startup
instead of waiting for the normal interval.

Third trap, knowing how to recognise an unreachable source. By declaring a
non-routable address, the line does appear but with `Reach` at 0 and the `?`
marker:

```text
^? 192.0.2.1                     0   7     0     -     +0ns[   +0ns] +/-    0ns
```

A listed source is therefore not a source that answers. `chronyc activity`
summarises the situation (`5 sources online`), and a healthy clock shows at
least one `^*`.

Finally, keep in mind the difference between running and being enabled.
`systemctl start` only concerns the current session, `systemctl enable`
registers the service at boot: the two are controlled separately, with
`systemctl is-active chronyd` and `systemctl is-enabled chronyd`. And the final
proof, the one that is beyond discussion, fits in one line of `timedatectl`:
`System clock synchronized: yes`.

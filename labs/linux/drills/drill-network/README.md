# Drill — static networking

**4 tasks, 100 points, 20 minutes. No hints.** Shared between RHCSA and LFCS:
the subject names no tool, you use the one of your distribution (`nmcli` on
AlmaLinux, `netplan` on Ubuntu). Everything happens on the dedicated interface
`lab0`, **never** on the management interface, and everything is checked **after
a network reload**.

## What a drill is

A drill is not a lab. There is no course here, and that is deliberate: you are
in exam conditions. You are given a brief, a stopwatch and a machine, and you
have to find on your own the gestures you have already practised.

The difference with a lab comes down to three points:

- **no hint is available**, not even against points;
- **time counts**: 20 minutes for four tasks is the pace of the exam, not that of
  learning;
- **the tasks are independent**. If one resists, move on to the next and come
  back to it: an untreated task costs less than a stopwatch exhausted on the
  first one.

The pass mark is set at **70 points out of 100**.

## What you need to know before attempting it

This drill separates two things that are often confused: configuring an
interface, and making that configuration live after a reload. If one of the
subjects below is not familiar to you, play the corresponding lab **first**: you
will find there the course, the hints and the right to make mistakes that the
drill will not give you.

| What the drill exercises | The lab where it is taught |
|---|---|
| Setting a static address in a profile that survives the reload | `l4-network-static-persist` |
| Understanding why a command typed by hand does not persist | `l4-network-static-persist` |
| Reading the real state of a link and of a route | `l4-network-troubleshoot` |
| Resolving a name without a DNS server, and proving it with `getent hosts` | `l4-network-troubleshoot` |

On the Ubuntu side, `netplan` is the subject of the `lfcs-netplan-static` lab.
Careful: its README does not contain an on-site course yet, it points to the
online guide.

## Getting into exam conditions

Start the stopwatch before opening the brief, not after. Twenty minutes go by
fast, and the first exam reflex is to **read the four tasks first** in order to
spot the ones that are handled in one command.

Three precautions specific to networking:

- **first identify the interface not to touch**. Its name changes depending on
  the distribution and the hypervisor, so do not guess it: ask the system with
  `ip route get 1.1.1.1`, which gives you the interface that carries your
  session. Everything you do afterwards happens elsewhere. A management interface
  cut off means the machine is lost, and the drill with it;
- **configured is not active**. Writing an address into a profile or into a YAML
  file does not put it in place, and applying it by hand does not write it
  anywhere. The check reloads the network before looking: get into the habit of
  reloading yourself, then rereading the state with `ip addr show` and `ip
  route`, never by rereading your own file;
- **name resolution is not tested with `dig`**. `dig` queries a server and
  ignores the local resolution: it is `getent hosts` that follows the same path
  as the applications, and therefore the only verdict that counts here.

A detail that costs points on Ubuntu: a network configuration file that is too
permissive is refused or flagged. Check its permissions before concluding that
your syntax is at fault.

## Afterwards

The correction does not only say how many points you got: it says **which task**
failed and **what the system contained** at the moment of the check. Reread it
before playing again.

A drill is meant to be replayed. The second attempt serves to measure what you
retained from your mistakes, not to memorise answers: the exact values matter
less than the gestures, which do transpose to any brief.

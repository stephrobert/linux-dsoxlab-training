# Context — the Debian firewall: ufw

On Debian/Ubuntu the friendly front-end to the firewall is **`ufw`** (Uncomplicated
FireWall). A web service must be reachable, so you'll open `http` and turn the
firewall on — while keeping your SSH way in.

The point: `ufw` is the Debian counterpart to `firewall-cmd` — same idea,
deliberately minimal syntax. The firewall has an on/off state of its own,
separate from the rules it holds: both count, and the order in which you deal
with them decides whether you keep your session or not.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/

# Context — the Debian firewall: ufw

On Debian/Ubuntu the friendly front-end to the firewall is **`ufw`** (Uncomplicated
FireWall). A web service must be reachable, so you'll open `http` and turn the
firewall on — while keeping your SSH way in.

Your mission, on the Ubuntu VM:

1. Allow the **`http`** service: `sudo ufw allow http` (or `ufw allow 80/tcp`).
2. **Enable** the firewall: `sudo ufw enable`.
3. **Never remove `OpenSSH`** — it's already allowed; keep it so you're not locked
   out.

The point: `ufw allow <service|port>` adds a rule, `ufw enable` activates the
firewall (and makes it start at boot), `ufw status` lists the rules. It's the
Debian counterpart to `firewall-cmd` — same idea, simpler syntax.

Method in the companion guide:
https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/

# Context — the interface is configured but dead

A connection called `lab-net` exists on interface `lab1` with a correct static
address, yet the interface carries no IP and it won't come back after a reboot.
Something's off with its state — find it and bring the link back to life.

You work on `lab1`. **Never touch the management interface** — the one carrying
your default route: it is your link to the box.

The point: a connection can be fully configured and still carry nothing, and one
that comes up today will not necessarily come up at the next boot. Those are two
distinct states, both readable in what NetworkManager reports: to be read, not
guessed.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/

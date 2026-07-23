# Context — hand out just enough sudo

The operations team needs to restart services, but they must **not** get full
root. This is delegation with least privilege: letting the `operators` group run
`systemctl` — and only that — without a password.

The point: sudo policy is split into independent fragments rather than piled into
one file, and it is the list of allowed commands that makes the delegation worth
anything. A syntax error there is catastrophic: it gets validated before it is
applied, never after.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/

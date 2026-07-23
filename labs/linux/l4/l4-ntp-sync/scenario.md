# Context — put the clock back in sync

This host drifted: its timezone is wrong, NTP is off and `chronyd` isn't even
running. Logs get confusing timestamps and TLS handshakes start failing when the
clock is off. Bring it back — and make it hold across a reboot.

The point: a timezone is only a display convention, it does not move the instant.
What matters lies elsewhere, in a question that is asked at boot as much as right
now: does this host keep its clock from the network? That lasting state is what
gets checked, not the commands you typed.

Method in the companion guide:
https://blog.stephane-robert.info/docs/services/reseau/chrony/

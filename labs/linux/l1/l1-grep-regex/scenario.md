# Context — read an access log with grep alone

You have `acces.log`, ten lines of the shape `IP - METHOD /path CODE`. Using only
`grep` and regular expressions, extract four exact facts into separate files: the
server errors, everything that is not a success, the distinct client IPs, and how
many POST requests there were.

The point: the same file yields four different facts depending on how you
question it. Selecting lines, excluding them, extracting only part of a line, or
returning nothing but a number are four distinct uses of a single tool.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/

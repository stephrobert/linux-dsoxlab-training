# Context — read an access log with grep alone

You have `acces.log`, ten lines of the shape `IP - METHOD /path CODE`. Using only
`grep` and regular expressions, extract four exact facts into separate files: the
server errors, everything that is not a success, the distinct client IPs, and how
many POST requests there were.

Your mission — produce, in the work directory:

1. `erreurs5xx.txt` — only the lines whose HTTP code is a **5xx** (server error).
2. `sans-200.txt` — every line **except** the `200` ones (invert match).
3. `ips.txt` — the **distinct** client IP addresses, sorted.
4. `nb-post.txt` — the **count** of POST requests.

The point: a regex anchored to the end of the line (`$`), a character class
(`[0-9]`), invert match (`-v`), extract-only (`-o`) and count (`-c`) each pull a
different fact from the same file.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/

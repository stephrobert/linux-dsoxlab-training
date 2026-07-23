# Context — read a TLS certificate

Someone handed you `serveur.crt` and asks the basic questions every admin must
answer from the command line: who is it for, when does it expire, what is its
fingerprint, and what public key does it carry.

The point: `openssl` reads all of it offline, from the file, with no server
running. Each question has its own selector, which you have to go and find. The
tests re-run openssl on the certificate and compare, so a hand-typed or empty
file fails.

Method in the companion guide:
https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/

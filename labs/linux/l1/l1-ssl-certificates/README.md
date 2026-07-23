# Lab — inspect a TLS certificate

## Reminder

[**TLS diagnostics on the companion guide**](https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/)

`openssl x509 -in cert -noout <selector>` reads a certificate offline:
`-subject` (who), `-issuer` (signed by), `-dates` (validity window),
`-fingerprint -sha256` (a stable identity hash), `-pubkey` (the embedded public
key). No server needed.

## The course

The examples below build then inspect the certificates of an internal API
called `api.interne.test`, in the `~/pki-atelier` directory: the challenge will
hand you another certificate, carrying another name, and will ask you for other
output files. The point is to learn how to read and check a certificate, not to
copy a line.

Everything happens **offline**, with no network and no public authority: that
is the only way to get a reproducible exercise. The outputs reproduced here
come from an AlmaLinux 10 with **OpenSSL 3.5.5**; an older version may lay the
text out differently. The fingerprints, serial numbers and dates will obviously
differ on your side, since your keys will differ: it is the **shape** of the
outputs you must recognise, not their content.

```bash
mkdir -p ~/pki-atelier && cd ~/pki-atelier
openssl version
# OpenSSL 3.5.5 27 Jan 2026 (Library: OpenSSL 3.5.5 27 Jan 2026)
```

### Three objects not to be confused

The whole exercise follows from this vocabulary:

- The **private key** is the server's secret. It never leaves the machine.
- The **CSR** (*Certificate Signing Request*) is a **request**: it contains the
  server's identity and its **public key**, and goes to an authority.
- The **certificate** is the **signed** CSR. It attests that an authority has
  validated that this public key really belongs to this identity.

A **self-signed** certificate short-circuits the authority: the server signs
its own certificate. No client trusts it by default. An **internal authority**
(CA) solves this: you trust it once, and it then signs all the certificates of
the house.

### Generate a private key

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out api.key
```

The command spits a shower of dots on standard error while it looks for prime
numbers: this is normal, it is not an error message.

One detail theory forgets: the produced file is **already** `0600`, whereas the
machine's `umask` (`0022`) would give `0644` to an ordinary file.

```bash
umask                                 # 0022
touch temoin.txt ; stat -c '%a %n' temoin.txt api.key
```

```text
644 temoin.txt
600 api.key
```

`chmod 600 api.key` remains a good habit (it catches a key that was copied or
moved), but it fixes nothing here: `openssl genpkey` set the permissions
itself. A private key readable by everyone allows the service to be
impersonated: you do not copy it from one server to another, and you never put
it under version control.

### Create a signing request, and its `subjectAltName`

The decisive field is the **`subjectAltName`** (SAN): it is the one that lists
the names the certificate covers. `-subj` fills in the identity without
interactive questions, `-addext` adds the extension.

```bash
openssl req -new -key api.key -out api.csr \
  -subj "/C=FR/O=Atelier Interne/CN=api.interne.test" \
  -addext "subjectAltName=DNS:api.interne.test,DNS:api-v2.interne.test"

openssl req -in api.csr -noout -subject
openssl req -in api.csr -noout -text | grep -A1 "Subject Alternative Name"
openssl req -in api.csr -noout -verify
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
                X509v3 Subject Alternative Name:
                    DNS:api.interne.test, DNS:api-v2.interne.test
Certificate request self-signature verify OK
```

Note the `C=FR` spelling, with no space around the `=`. Many documents show the
spaced form `C = FR`: it is the same information, formatted differently, and
the `-nameopt` option switches from one to the other.

```bash
openssl req -in api.csr -noout -subject
openssl req -in api.csr -noout -subject -nameopt oneline
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
subject=C = FR, O = Atelier Interne, CN = api.interne.test
```

Practical consequence: a `grep 'CN = api.interne.test'` written from a piece of
documentation will find nothing on this machine. Never assume the spacing of an
output, look at it.

### The shortcut: the self-signed certificate

For a local test, `-x509` directly produces a certificate, with no CSR and no
authority:

```bash
openssl req -x509 -key api.key -out api-autosigne.crt -days 365 \
  -subj "/C=FR/O=Atelier Interne/CN=api.interne.test" \
  -addext "subjectAltName=DNS:api.interne.test"
```

Look at what was written into it, it is not what you asked for:

```bash
openssl x509 -in api-autosigne.crt -noout -text | sed -n '/X509v3 extensions/,/Signature Algorithm/p'
```

```text
        X509v3 extensions:
            X509v3 Subject Key Identifier:
                58:22:CD:6C:FE:5F:AB:E9:92:17:20:4D:76:6B:D8:12:12:C7:89:29
            X509v3 Authority Key Identifier:
                58:22:CD:6C:FE:5F:AB:E9:92:17:20:4D:76:6B:D8:12:12:C7:89:29
            X509v3 Basic Constraints: critical
                CA:TRUE
            X509v3 Subject Alternative Name:
                DNS:api.interne.test
```

`openssl req -x509` marks the certificate **`CA:TRUE`** by default: your
service certificate is, technically, a certificate authority. For a leaf
certificate, force the opposite:

```bash
openssl req -x509 -key api.key -out api-feuille.crt -days 365 \
  -subj "/C=FR/O=Atelier Interne/CN=api.interne.test" \
  -addext "subjectAltName=DNS:api.interne.test" \
  -addext "basicConstraints=critical,CA:FALSE"

openssl x509 -in api-feuille.crt -noout -ext basicConstraints
```

```text
X509v3 Basic Constraints: critical
    CA:FALSE
```

Leaf or not, a self-signed certificate is rejected at validation, and that is
the expected behaviour:

```bash
openssl verify api-feuille.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 18 at 0 depth lookup: self-signed certificate
error api-feuille.crt: verification failed
```

The **18** code of the `Verify return code` you will meet in a TLS diagnostic
can therefore be reproduced locally, without any server.

### Set up an in-house authority

A CA is a key and a certificate **marked as an authority**. The key is longer,
because it protects the whole chain.

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out ca-atelier.key

openssl req -x509 -key ca-atelier.key -out ca-atelier.crt -days 3650 \
  -subj "/C=FR/O=Atelier Interne/CN=Autorite Atelier" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"

openssl x509 -in ca-atelier.crt -noout -ext basicConstraints,keyUsage
```

```text
X509v3 Basic Constraints: critical
    CA:TRUE
X509v3 Key Usage: critical
    Certificate Sign, CRL Sign
```

`CA:TRUE` is what allows this certificate to sign others, `keyCertSign` is what
declares that use of the key.

Mind the syntax: several extensions are requested as **one comma-separated
list**. Repeating the option does not add them up, it keeps only the last one,
silently:

```bash
openssl x509 -in ca-atelier.crt -noout -ext basicConstraints -ext keyUsage
```

```text
X509v3 Key Usage: critical
    Certificate Sign, CRL Sign
```

The `basicConstraints` has disappeared from the output without the slightest
warning. This is the kind of detail that leads you to conclude wrongly that an
extension is missing.

### Signing, and the trap of the lost `subjectAltName`

The authority signs the CSR. Make the mistake first, it is instructive:

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-sans-san.crt -days 365
```

```text
Certificate request self-signature ok
subject=C=FR, O=Atelier Interne, CN=api.interne.test
```

```bash
openssl x509 -in api-sans-san.crt -noout -ext subjectAltName
```

```text
No extensions in certificate
```

The CSR's SAN has been **lost**. Two traps in this single output line:

- the message is misleading: the certificate **does** have extensions (it
  inherited a `Subject Key Identifier` and an `Authority Key Identifier`,
  visible with `-text`), just not the one that was asked for;
- the return code is **`0`**. A script testing `if openssl x509 -ext
  subjectAltName …` will conclude that all is well. Test the output, not the
  code.

Correct signing requires **`-copy_extensions copy`**, which copies the CSR's
extensions into the certificate:

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api.crt -days 365 -copy_extensions copy

openssl x509 -in api.crt -noout -subject -issuer
openssl x509 -in api.crt -noout -ext subjectAltName
openssl verify -CAfile ca-atelier.crt api.crt
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
issuer=C=FR, O=Atelier Interne, CN=Autorite Atelier
X509v3 Subject Alternative Name:
    DNS:api.interne.test, DNS:api-v2.interne.test
api.crt: OK
```

`-CAcreateserial` also creates a `ca-atelier.srl` file that remembers the
serial number: two certificates from the same authority must never share the
same one.

Without `-CAfile`, the same verification fails, for lack of knowing whom to
trust:

```bash
openssl verify api.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 20 at 0 depth lookup: unable to get local issuer certificate
error api.crt: verification failed
```

This is code **20**, `unable to get local issuer certificate`: the issuer
cannot be found. A client meets the same code when facing a server that does
not serve its chain. On the server side, you therefore serve the leaf **and**
the authority concatenated in a single file:

```bash
cat api.crt ca-atelier.crt > fullchain.pem
grep -c "BEGIN CERTIFICATE" fullchain.pem      # 2
```

### Reading a certificate: the basic questions

A certificate is always read the same way, with `-noout` (which suppresses the
display of the PEM block) followed by a selector. No server is needed:

```bash
openssl x509 -in api.crt -noout -subject -issuer -dates
openssl x509 -in api.crt -noout -fingerprint -sha256
```

```text
subject=C=FR, O=Atelier Interne, CN=api.interne.test
issuer=C=FR, O=Atelier Interne, CN=Autorite Atelier
notBefore=Jul 22 14:17:01 2026 GMT
notAfter=Jul 22 14:17:01 2027 GMT
sha256 Fingerprint=4C:48:77:38:83:55:DB:12:11:6D:E3:CB:9E:3A:E4:65:89:3F:81:11:17:6C:AC:D0:49:4F:8A:AD:85:AA:20:D6
```

`subject` and `issuer` differ: this certificate really was signed by a third
party. When both are identical, it is a self-signed one. The **SHA-256
fingerprint** is a digest of the whole certificate: it changes at the slightest
modified byte, which makes it a stable identifier for comparing two copies or
recording what has been deployed.

The certificate finally carries the **public key** matching the private key.
This can be proven by comparing the three extractions:

```bash
openssl x509 -in api.crt  -noout -pubkey  | openssl sha256
openssl pkey -in api.key  -pubout         | openssl sha256
openssl req  -in api.csr  -noout -pubkey  | openssl sha256
```

```text
SHA2-256(stdin)= 1adee5c51f71a45a806a021d4501efbc57d9e55fb176e8c36ae46fad2180220a
SHA2-256(stdin)= 1adee5c51f71a45a806a021d4501efbc57d9e55fb176e8c36ae46fad2180220a
SHA2-256(stdin)= 1adee5c51f71a45a806a021d4501efbc57d9e55fb176e8c36ae46fad2180220a
```

The three digests are identical: the key, the request and the certificate do
talk about the same cryptographic material. The authority's own digest is
different, which is reassuring:

```text
SHA2-256(stdin)= f91e51da80efdac93543a5409a8e5ad7f66008f3f82228bc7e257720282e90c2
```

This is the check to run when a service refuses to start, complaining about a
key that does not match its certificate.

### Dates, the most frequent trap

A certificate is only valid between `notBefore` and `notAfter`. Let us
manufacture the two classic failures. `-not_before` and `-not_after` take a
date in the `YYYYMMDDHHMMSSZ` format.

These two options are **recent**: they exist on this machine's OpenSSL 3.5, but
not on an OpenSSL 3.0 (Debian 12, Ubuntu 22.04), where `openssl x509 -help`
does not mention them. On such a machine, the equivalents are `-startdate` and
`-enddate` of the `openssl ca` subcommand. Check first what you have:

```bash
openssl x509 -help 2>&1 | grep -E 'not_before|not_after'
```

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-expire.crt -copy_extensions copy \
  -not_before 20240101000000Z -not_after 20240401000000Z

openssl x509 -in api-expire.crt -noout -dates
openssl verify -CAfile ca-atelier.crt api-expire.crt
```

```text
notBefore=Jan  1 00:00:00 2024 GMT
notAfter=Apr  1 00:00:00 2024 GMT
C=FR, O=Atelier Interne, CN=api.interne.test
error 10 at 0 depth lookup: certificate has expired
error api-expire.crt: verification failed
```

The other failure, rarer and far more confusing, happens when the client's
clock is behind or when a certificate was issued ahead of time:

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-futur.crt -copy_extensions copy \
  -not_before 20300101000000Z -not_after 20310101000000Z

openssl verify -CAfile ca-atelier.crt api-futur.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 9 at 0 depth lookup: certificate is not yet valid
error api-futur.crt: verification failed
```

For monitoring, `-checkend N` answers with an **exit code**: `0` if the
certificate is still valid in `N` seconds, `1` otherwise.

```bash
openssl x509 -in api.crt -noout -checkend 0 ; echo "code $?"
openssl x509 -in api-expire.crt -noout -checkend 0 ; echo "code $?"
```

```text
Certificate will not expire
code 0
Certificate will expire
code 1
```

On a certificate issued for 10 days, the question "will it hold for 30 days?"
is asked like this:

```bash
openssl x509 -req -in api.csr -CA ca-atelier.crt -CAkey ca-atelier.key \
  -CAcreateserial -out api-court.crt -days 10 -copy_extensions copy

openssl x509 -in api-court.crt -noout -dates
openssl x509 -in api-court.crt -noout -checkend 2592000 ; echo "code $?"
```

```text
notBefore=Jul 22 14:18:13 2026 GMT
notAfter=Aug  1 14:18:13 2026 GMT
Certificate will expire
code 1
```

One limit of `-checkend` deserves to be known, because it goes unnoticed. Run
it again on the certificate that is not yet valid:

```bash
openssl x509 -in api-futur.crt -noout -checkend 0 ; echo "code $?"
```

```text
Certificate will not expire
code 0
```

The certificate is **not yet valid**, and `-checkend` still answers `0`. It
only looks at `notAfter`. Monitoring that only tests `-checkend` will therefore
let an unusable certificate through: it is `openssl verify` that decides.

### What `openssl verify` refuses, and what it lets through

Two cases deserve to be tried rather than taken on trust.

**First case: a certificate with no `subjectAltName`.** The rule read
everywhere is that it is refused, the `CN` alone being ignored. Take
`api-sans-san.crt` again, whose SAN was lost but whose `CN` is correct:

```bash
openssl verify -CAfile ca-atelier.crt -verify_hostname api.interne.test api-sans-san.crt
```

```text
api-sans-san.crt: OK
```

Accepted. This machine's OpenSSL chain (and therefore `curl`, which relies on
it) falls back to the `CN` when no DNS-type SAN is present. This can be
confirmed with a real client, by serving the certificate on the loopback:

```bash
openssl s_server -accept 8443 -cert api-sans-san.crt -key api.key -www -quiet &
curl -sS -o /dev/null -w 'http=%{http_code}\n' --cacert ca-atelier.crt \
  --resolve api.interne.test:8443:127.0.0.1 https://api.interne.test:8443/
```

```text
http=200
```

What this means: the companion guide recalls that a certificate without a SAN
is refused, modern clients ignoring the `CN`. That is true of browsers, which
ship their own validator, but **not** of the AlmaLinux 10 command-line tools,
which still accept it. So do not count on `openssl verify` or on `curl` to
detect a missing SAN: read it, with `-ext subjectAltName`. And always set the
SAN, because the day the service is called from a browser, it breaks.

The real refusal comes when the requested name **is covered nowhere**:

```bash
openssl verify -CAfile ca-atelier.crt -verify_hostname autre.interne.test api.crt
```

```text
C=FR, O=Atelier Interne, CN=api.interne.test
error 62 at 0 depth lookup: hostname mismatch
error api.crt: verification failed
```

And on the client side, by serving `api.crt` but calling it under another name:

```bash
openssl s_server -accept 8443 -cert api.crt -key api.key -www -quiet &
curl -sS -o /dev/null --cacert ca-atelier.crt \
  --resolve autre.interne.test:8443:127.0.0.1 https://autre.interne.test:8443/
```

```text
curl: (60) SSL: no alternative certificate subject name matches target hostname 'autre.interne.test'
```

Above all, remember that `openssl verify` **does not check the hostname**
unless you ask it to: without `-verify_hostname`, it validates the chain and
nothing else. An `OK` therefore does not mean "this certificate is suitable for
this domain".

**Second case: an authority that is not one.** Let us build a certificate
marked `CA:FALSE` and use it to sign:

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out fausse-ca.key
openssl req -x509 -key fausse-ca.key -out fausse-ca.crt -days 365 \
  -subj "/C=FR/O=Atelier Interne/CN=Fausse Autorite" \
  -addext "basicConstraints=critical,CA:FALSE"

openssl x509 -req -in api.csr -CA fausse-ca.crt -CAkey fausse-ca.key \
  -CAcreateserial -out api-fausse.crt -days 365 -copy_extensions copy
```

```text
Certificate request self-signature ok
subject=C=FR, O=Atelier Interne, CN=api.interne.test
```

The signature **succeeds**: `openssl x509 -req` does not ask the issuer whether
it is allowed to sign, it signs. The refusal only comes at verification time,
on the client:

```bash
openssl verify -CAfile fausse-ca.crt api-fausse.crt
```

```text
C=FR, O=Atelier Interne, CN=Fausse Autorite
error 79 at 1 depth lookup: invalid CA certificate
error api-fausse.crt: verification failed
```

Two details to read in this message: `at 1 depth` designates the **second**
link in the chain (the issuer, not the leaf at depth `0`), and the subject
shown is that of the fake authority. It is the issuer's certificate that is at
fault, not the service's. A certificate issued by a malformed authority is
therefore **unusable**, even though its creation produced no error at all.

### Getting the authority trusted by clients

So that clients accept your authority's certificates without warning, you
install **`ca-atelier.crt`** (never the key) in the system trust store:

```bash
# RHEL, AlmaLinux
sudo cp ca-atelier.crt /etc/pki/ca-trust/source/anchors/atelier-interne.crt
sudo update-ca-trust
trust list | grep "Autorite Atelier"

# Debian, Ubuntu (the .crt extension is mandatory, otherwise the file is ignored)
sudo cp ca-atelier.crt /usr/local/share/ca-certificates/atelier-interne.crt
sudo update-ca-certificates
```

These two commands modify a store shared by the whole machine, including by the
administration tools. On a shared work machine, it is better to stick to
`--cacert` (for `curl`) and `-CAfile` (for `openssl`), which give the same
result for a test, with no side effect and no privilege.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `error 18 ... self-signed certificate` | self-signed certificate, no authority behind it |
| `error 20 ... unable to get local issuer certificate` | the issuer cannot be found: incomplete chain, or `-CAfile` forgotten |
| `error 10 ... certificate has expired` | `notAfter` passed, or client clock ahead |
| `error 9 ... certificate is not yet valid` | `notBefore` in the future, or client clock behind |
| `error 62 ... hostname mismatch` | the requested name is neither in the SAN nor in the `CN` |
| `error 79 ... invalid CA certificate` | the issuer is not marked `CA:TRUE` |
| `curl: (60) SSL: no alternative certificate subject name matches...` | same cause as the 62, seen from the client |
| `No extensions in certificate` on `-ext subjectAltName` | the requested extension is missing, often a `-copy_extensions copy` forgotten at signing time |
| A requested extension does not appear in the output | a repeated `-ext` keeps only the last one, write `-ext a,b` |
| The service says the key does not match the certificate | compare `openssl x509 -pubkey` and `openssl pkey -pubout`, digested with `sha256` |
| `openssl verify` says `OK` but the browser refuses | no SAN: `openssl` falls back to the `CN`, the browser does not |
| A self-signed certificate behaves like an authority | `openssl req -x509` sets `CA:TRUE` by default, force `CA:FALSE` |

### Undoing the demonstration

Everything fits in one directory, there is nothing to restore anywhere else:

```bash
pkill -x openssl            # if an openssl s_server is still running
rm -rf ~/pki-atelier
```

If you added the authority to the trust store, remove it too, otherwise the
machine will keep trusting a key that is lying around:

```bash
sudo rm -f /etc/pki/ca-trust/source/anchors/atelier-interne.crt && sudo update-ca-trust
```

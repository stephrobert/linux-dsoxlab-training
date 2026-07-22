# Lab — reverse proxy & load balancing with HAProxy

## Reminder

[**HAProxy on the companion guide**](https://blog.stephane-robert.info/docs/services/reseau/haproxy/)

HAProxy is an L7 proxy: a `frontend` binds a port, a `backend` lists the real
`server`s and `balance`s the load between them. `haproxy -c -f <cfg>` validates
the config before you start the service.

## The course

The examples in this course are not those of the challenge: they build a proxy
with **another tool** (nginx), on **other ports**, in front of **other
backends**. That is deliberate: the mechanics of a reverse proxy are the same
everywhere, only the keywords change, and what is demonstrated here transposes
to the tool of the challenge, whose syntax is described in the guide above.

Every output below comes from an AlmaLinux 10.2 VM (`10.10.30.13`), queried from
a client machine (`10.10.30.1`).

### Reverse proxy or load balancer: what separates them

The two terms are often confused. The
[Reverse proxy](https://blog.stephane-robert.info/docs/services/reseau/reverse-proxy/)
guide tells them apart this way:

| Concept | What it does |
|---|---|
| **Reverse proxy** | HTTP(S) entry point: TLS, routing, headers, security |
| **Load balancer** | Spreads the traffic across several servers (L4 or L7) |

Remember the simple rule: a reverse proxy relays to **one** service, a load
balancer distributes between **several**. In practice most tools do both, and
going from one to the other takes two lines.

### Building two backends without installing anything

You need at least two services that answer differently. Python's `http.server`
module, present on the image, is enough:

```bash
mkdir -p ~/workshop/alpha ~/workshop/beta
echo "response from server alpha" > ~/workshop/alpha/index.html
echo "response from server beta"  > ~/workshop/beta/index.html

cd ~/workshop
setsid nohup python3 -m http.server 9510 --bind 127.0.0.1 --directory alpha > alpha.log 2>&1 &
setsid nohup python3 -m http.server 9511 --bind 127.0.0.1 --directory beta  > beta.log  2>&1 &
```

`--bind 127.0.0.1` limits the listening to the loopback: the backends can only
be reached by the proxy, never directly from the network. That is already a
benefit of the reverse proxy, it hides the real servers.

```bash
curl -s http://127.0.0.1:9510/ ; curl -s http://127.0.0.1:9511/
```

```text
response from server alpha
response from server beta
```

Both backends answer: everything that follows is diagnosed against that known
starting point.

### Installing the proxy and relaying to a single backend

On the AlmaLinux 10 image of the lab, no web server is present:

```bash
rpm -q nginx haproxy httpd
dnf -q repoquery --qf "%{name} %{version} %{reponame}" nginx haproxy httpd
```

```text
package nginx is not installed        [... same for haproxy and httpd ...]
nginx 1.26.3 appstream
haproxy 3.0.5 appstream
httpd 2.4.63 appstream
```

All three are in **AppStream**, the distribution repository: no third-party
repository, no EPEL is needed. This course installs `nginx`, whose configuration
makes the relay / balancing difference particularly readable.

```bash
sudo dnf install -y nginx && nginx -v    # nginx version: nginx/1.26.3
```

The minimal configuration of a reverse proxy fits in one file dropped in
`/etc/nginx/conf.d/`:

```nginx
# /etc/nginx/conf.d/workshop-proxy.conf
server {
    listen 8008;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:9510;
        proxy_set_header Host $host;
    }
}
```

The listening port is not chosen at random: SELinux only allows a web server to
listen on a list of known ports, and `8008` is one of them.

```bash
sudo semanage port -l | grep ^http_port_t
```

```text
http_port_t   tcp   80, 81, 443, 488, 8008, 8009, 8443, 9000
```

You validate **before** starting, a reflex that holds for any proxy:

```bash
sudo nginx -t     # configuration file /etc/nginx/nginx.conf test is successful
sudo systemctl start nginx
```

### The three obstacles, in order

On a distribution of the RHEL family, three barriers stand between the client
and the backend, to be handled **in that order**: as long as the firewall
blocks you see nothing of SELinux, and as long as SELinux blocks you see nothing
of the configuration.

**Obstacle 1, the firewall.** From the client machine:

```bash
curl -sS --max-time 5 http://10.10.30.13:8008/
```

```text
curl: (7) Failed to connect to 10.10.30.13 port 8008 after 0 ms: Could not connect to server
```

Signature: an error **on the client side**, immediate ("after 0 ms": the port is
rejected, not silently filtered), and **nothing** in the proxy logs, which the
request never reached. Open the port, in **runtime only**:

```bash
sudo firewall-cmd --add-port=8008/tcp     # success
sudo firewall-cmd --list-ports            # 8008/tcp
sudo firewall-cmd --permanent --list-ports # (empty)
```

Without `--permanent`, the rule disappears at the next `firewall-cmd --reload`
or at reboot: perfect for a demonstration, not enough for a service that must
survive the reboot. **Never touch the `ssh` service of the zone**, it is your
only access to the machine.

**Obstacle 2, SELinux.** The port is open, the request arrives, and the proxy
answers `HTTP/1.1 502 Bad Gateway`. Its error log names the culprit:

```bash
sudo tail -1 /var/log/nginx/error.log
```

```text
[crit] 13631#13631: *1 connect() to 127.0.0.1:9510 failed (13: Permission denied)
while connecting to upstream, client: 10.10.30.1, server: _, request: "GET / HTTP/1.1",
upstream: "http://127.0.0.1:9510/", host: "10.10.30.13:8008"
```

`Permission denied` on a `connect()` to the loopback makes no sense from a Unix
point of view: it is the mark of SELinux. The audit log confirms it:

```bash
sudo ausearch --input /var/log/audit/audit.log -m AVC | grep name_connect | tail -1
```

```text
avc: denied { name_connect } for pid=13631 comm="nginx" dest=9510
scontext=system_u:system_r:httpd_t:s0 tcontext=system_u:object_r:unreserved_port_t:s0
```

A web server runs in the `httpd_t` domain, and by default that domain does not
have the right to open an outgoing connection to an arbitrary port. The boolean
that lifts this restriction is documented in the
[SELinux](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)
guide:

```bash
getsebool httpd_can_network_connect     # httpd_can_network_connect --> off
sudo setsebool httpd_can_network_connect on
curl -sS http://10.10.30.13:8008/       # response from server alpha
```

Without `-P`, the change lives in memory and will be lost at reboot: that is
what you want for a demonstration, you do not rewrite the policy of the machine.
A consequence worth knowing, a boolean set without `-P` **does not appear** in
`semanage boolean -l -C`, which only lists the persistent customisations; to
check the real state, `getsebool` is what you must query.

**Obstacle 3, the configuration.** Let us deliberately point the proxy at a port
where nobody listens. The HTTP answer is the **same** (502), the log is not:

```text
[error] connect() failed (111: Connection refused) while connecting to upstream,
client: 10.10.30.1, server: _, upstream: "http://127.0.0.1:9599/"
```

Hence the diagnostic table, to keep in mind:

| What you see | Proxy log | Cause |
|---|---|---|
| `curl: (7) Failed to connect` | nothing at all | firewall |
| `502 Bad Gateway` | `(13: Permission denied)` | SELinux |
| `502 Bad Gateway` | `(111: Connection refused)` | backend down or wrong port in the config |

The two `errno` say everything: **13** means "you are forbidden", **111** means
"nobody answers".

### Moving to load balancing, and proving it

The reverse proxy relays to a hard-coded address. To balance, you declare a
**group** of servers and relay to that group:

```nginx
# /etc/nginx/conf.d/workshop-proxy.conf
upstream workshop_pool {
    server 127.0.0.1:9510;
    server 127.0.0.1:9511;
}

server {
    listen 8008;
    server_name _;

    location / {
        proxy_pass http://workshop_pool;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    }
}
```

Only one thing changed in nature: `proxy_pass` no longer targets an address but
a group name. That is the switch every proxy offers, under other keywords. And a
configuration proves nothing as long as the balancing has not been **observed**:
ten requests are enough.

```bash
sudo nginx -t && sudo systemctl reload nginx
for i in $(seq 1 10); do curl -sS http://10.10.30.13:8008/; done
```

```text
response from server alpha
response from server beta
[... 8 lines, strict alternation ...]
```

A trap observed during this test: launched **during** the `reload`, the same
loop gave 8 `alpha` answers for 2 `beta`. For the duration of the reload, two
generations of worker processes coexist, each with its own rotation counter.
Measure once the reload is finished.

Second benefit, free of charge: stop `beta`, then send six requests again.

```bash
pkill -f "http.server 9511"
for i in $(seq 1 6); do curl -sS http://10.10.30.13:8008/; done
```

The six answers come from `alpha`, **no error is returned to the client**, and
the proxy explains what it did:

```text
[error] connect() failed (111: Connection refused) ... upstream: "http://127.0.0.1:9511/"
[warn]  upstream server temporarily disabled while connecting to upstream ...
```

The failing server is removed from the group automatically, then retried later:
the failure of a backend becomes invisible to the user.

### The X-Forwarded-For and X-Real-IP headers

This is the most frequent omission in production, and it does not show: it all
works, but **the application logs become unusable**. With a proxy in front, the
backend no longer opens a connection with the client but with the proxy. A
backend that prints the headers it receives shows it beyond argument, here a
request sent from `10.10.30.1` with no `proxy_set_header` at all:

```text
Host: 127.0.0.1:9512
[... Connection, User-Agent, Accept ...]
127.0.0.1 - - [22/Jul/2026 16:33:29] "GET / HTTP/1.0" 200 -
```

The backend believes that all its visitors come from `127.0.0.1` (last line, its
access log), and it has lost the host name requested by the client. With the
three directives of the previous configuration, the same request arrives like
this:

```text
Host: 10.10.30.13
X-Real-IP: 10.10.30.1
X-Forwarded-For: 10.10.30.1
[... Connection, User-Agent, Accept ...]
```

| Header | What it carries |
|---|---|
| `Host` | the host name requested by the client, otherwise the backend sees the address of the group |
| `X-Real-IP` | the address of the immediate client |
| `X-Forwarded-For` | the chain of addresses traversed, to which each proxy appends its own |

The `$proxy_add_x_forwarded_for` variable **appends** the address to the
existing `X-Forwarded-For` instead of overwriting it, which makes it possible to
trace a chain of several proxies. Security corollary: since any client can send
an `X-Forwarded-For`, only the value appended by **your** edge proxy is
trustworthy.

### Putting the machine back in order

A demonstration is undone entirely, in order: the processes, the package, then
the two system settings.

```bash
pkill -f "http[.]server"
sudo systemctl stop nginx
sudo dnf remove -y nginx
sudo firewall-cmd --remove-port=8008/tcp
sudo setsebool httpd_can_network_connect off
```

And above all, you check rather than assume:

```bash
sudo firewall-cmd --list-all          # ports: (empty), services: cockpit dhcpv6-client ssh
getsebool httpd_can_network_connect   # httpd_can_network_connect --> off
sudo semanage boolean -l -C           # no httpd_* line
ss -tlnp                              # only port 22 is still listening
```

Since the firewall was only changed at runtime, `--permanent` never moved. The
SELinux boolean, however, must be put back to `off` explicitly: uninstalling the
proxy does not change it. Same trap as a `sysctl` value set by hand, removing
what used it does not reset it.

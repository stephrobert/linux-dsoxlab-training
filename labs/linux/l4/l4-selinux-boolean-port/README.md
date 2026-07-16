# Lab — SELinux boolean and port labeling

> Prepare: `dsoxlab provision` then `dsoxlab run l4-selinux-boolean-port`

## Recap

[**SELinux on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/)

Under enforcing SELinux, you grant access without turning it off. **Booleans**
toggle predefined policy switches — `setsebool -P <bool> on` makes it persistent.
**Port labeling** lets a confined service bind a non-standard port —
`semanage port -a -t <type> -p tcp <port>`. Read with `getsebool` and
`semanage port -l`.

## Objectives

- `httpd_can_network_connect` is `on` and persistent;
- `8404/tcp` is labeled `http_port_t`.

## Validate

```bash
dsoxlab check l4-selinux-boolean-port
```

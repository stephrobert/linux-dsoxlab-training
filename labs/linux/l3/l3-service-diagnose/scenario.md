# Context — Systemd service stuck in crash loop

You are the on-call admin on **alma-rhcsa-1.lab**. The pager fires at
3 AM: an internal API service called **`demo-crashloop`** has been
**restarting in a loop** since last night's deployment.

The release ticket doesn't mention any code change. You suspect a
configuration or packaging issue.

The service is intentionally simple: a fake HTTP daemon that boots,
loads its config, then waits for requests. The pedagogical value is
entirely in the **diagnostic method**.

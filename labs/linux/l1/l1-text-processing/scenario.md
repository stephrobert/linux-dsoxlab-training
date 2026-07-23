# Context — turn a raw record file into facts

You have `ventes.csv`, eight `;`-separated records of the shape
`date;region;product;amount`. With the shell's text toolbox alone, turn it into
four exact artifacts: the distinct regions, the count of sales per region, the
grand total, and a comma-separated version.

The point: every tool in the chain does exactly one job. The whole difficulty is
picking the right one for each question, and chaining them in the right order.

Method in the companion guides:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/transformer-texte/

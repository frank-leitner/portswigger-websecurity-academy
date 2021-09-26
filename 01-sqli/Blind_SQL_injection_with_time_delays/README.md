# Lab: Blind SQL injection with time delays

Lab-Link: <https://portswigger.net/web-security/sql-injection/blind/lab-time-delays>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Known information

- vulnerable to blind SQL injection
- parameter: value of tracking cookie
- Result: No visible difference in page, time delay can be caused
- Goal: Cause a 10 seconds delay

## Query

The query will look something like

```sql
SELECT trackingId FROM someTable WHERE trackingId = '<COOKIE-VALUE>'
```

In example case, the cookie contains this content
`Cookie: TrackingId=Hhpmds8u7A7Wf4TH; session=CjLImZazM0kQSZvcI7rV4kieQhRygEzJ`

I will omit the complete cookie content from now on and only provide the string appended to the TrackingId value.

## Steps

### Confirm vulnerable parameter

Due to the type of vulnerability, on the page itself we can not distinguish whether the injection caused any reaction. This also makes finding an injection point more difficult, as simply injecting a single quote does not cause any reaction.

On the [cheat sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet), time dalay examples are given for multiple database engines. As we don't know which one to choose, simply attempt them one by one.

```text
Oracle: dbms_pipe.receive_message(('a'),10)
Microsoft: WAITFOR DELAY '0:0:10'
PostgreSQL: SELECT pg_sleep(10)
MySQL: SELECT sleep(10) 
```

The important thing is that the query must remain valid, as if it errors out we will not get any indication of it and may assume that the injection failed and move to the next database engine, when in fact the query was never executed.

I try to form the following query (ABC being the value of the tracking cookie).

```sql
SELECT trackingId FROM someTable WHERE trackingId = 'ABC' || (<CODE HERE>) || ''
```

The first character injected is the single quote after the ABC, than I concatenate the output of my code, followed by another concatenation with a single quote. For Oracle and PostgreSQL, the `||`s are used for concatenation, for Microsoft a `+` and for MySQL a single space.

Reaching the PostgreSQL syntax, the query takes a long time to finish: 10.126s. Usually the query takes about 100ms for me, so these additional 10 seconds come from the injection.

Reloading the page shows that the lab is solved.

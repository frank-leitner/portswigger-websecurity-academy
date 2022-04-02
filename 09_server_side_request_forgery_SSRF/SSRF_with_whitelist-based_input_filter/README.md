# Lab: SSRF with whitelist-based input filter

Lab-Link: <https://portswigger.net/web-security/ssrf/lab-ssrf-with-whitelist-filter>  
Difficulty: EXPERT  
Python script: [script.py](script.py)  

## Known information

- Applications uses an internal system to check stock availability
- Admin interface available at `http://localhost/admin`
- Some anti-SSRF features are in place
- Goals:
  - Access admin interface and delete user `carlos`

## Steps

### Analysis

As usual, the first step is to analyse the application. As no credentials are provided, only the public pages are available initially.

The stock check option uses again full URLs to reference the target of the stock check. By now it is clear that this is a bad idea as it is an invitation for abuse. If such functionality is required, only submit IDs and have the application figure out where to go to. After all, it is the application that sends these links to the client in the first place.

Using the trivial attempt `http://localhost/admin` results is an error:

![error_wrong_domain](img/error_wrong_domain.png)

Fortunately (for the attacker), the application tells me the reason for the denial: It must be at a certal domain.

URL parsing is difficult. Common sense indicates that it should be easy, but it is not. I just recalled a youtube video I once saw that had this as a main point... Found it, it is from [LiveOverflow](https://www.youtube.com/channel/UClcE-kVhqyiHCcjYwcpfj9w) and has the nice title  [HOW FRCKN' HARD IS IT TO UNDERSTAND A URL?! - uXSS CVE-2018-6128](https://www.youtube.com/watch?v=0uejy9aCNbI). It is about a universal XSS vulnerability, but it basically shows very nicely that URL parsing is everything but trivial.

But I digress...

### Enumerate whitelisted values

A URL consists of multiple parts: the protocol, optional credentials, the hostname, the path, query parameters and fragments.

An example is `http://username:password@example.com/path/to/ressource?query=parameter#fragmentInPage`

To split it up into its parts:

- Protocol: `http`
- Credentials: `username:password` (with the ':password' being optional as well)
- Hostname: `example.com`
- Path: `/path/to/ressource`
- Query: `query=parameter`
- Fragment: `fragmentInPage`

If I am able to find differences in the way the application parses a URL for the whitelisting and the backend server, than I am golden.

So I use the valid domain `stock.weliketoshop.net` and add other parts to it to see if the application appears to handle it correctly or not.

I assume that I don't have to paraphrase localhost with alternative values, as there is a dedicated lab for this i guess that it will not be necessary here. Still, there are nice lists of possible ways to [reference localhost](https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery).

#### Credentials

If the application only checks that the contains the whitelisted hostname after the protocol, I may be able to bypass it by using `http://stock.weliketoshop.net@localhost`. This will send a request to `localhost` using `stock.weliketoshop.net` as username.

However, the application validates it correctly and denies access based on the wrong hostname.

Using `http://user:pass@stock.weliketoshop.net:8080/product/stock/check?productId=1&storeId=1` reports the stock numbers, so this case appears to be parsed correctly.

#### Fragment

Another option is using the fragment part. Usually, the fragment is used to reference individual parts of the document, e.g. a specific `id` element within the page. If the application does not parse it correctly, than using `http://localhost#stock.weliketoshop.net` I may be able to send the request to `localhost` and referencing a non existing element there.

But again, the application validates it correctly when using `http://localhost#stock.weliketoshop.net:8080/product/stock/check?productId=1&storeId=1`

#### Query

Also the query part may be used to confuse the whitelist checking. However, the query parts are very common (e.g. the `?username=carlos` of the lab description), so it is less likely that it was forgotten.

Still worth trying, but using `http://localhost?x=stock.weliketoshop.net` does not lead to anything usful either.

### Encoding

What happens between me and the application?

Most of the parts of the URL sent is transferred to the application. However, the web server usually URLdecodes it beforehand so any URLencoded will not be present when the application parses it. However, if I URLencode it twice the server will strip one encoding away and send the second level of encoding to the application.

If this is not accounted for in the validation, than the whitelisting may see it as requests to `stock.weliketoshop.net` and send it down its network stack. If this value is interpreted differently within the network stack, than the requests may end up in a different location than the application whitelist anticipated.

Using the credentials part and double URLencoding the `@` to `http://stock.weliketoshop.net%2540localhost` still results in the by now well known error message. the same applies when using the `#`.

But when I start to mix-n-match these, things start to behave differently:

![ssrf_bypass](img/ssrf_bypass.png)

Here, the whitelist sees provided credentials (`localhost%23`) for the correct hostname and lets it pass. Down the road it is again decoded to `localhost`, which shows the page.

Not only is the shop website shown as result of the stock checker, it also includes a link to the admin panel, showing that local requests are automatically trusted as admins.

### Deleting user carlos

To be completely honest, this part puzzles me right now. Initially I tried to access the admin interface by various ways of encoding `/admin` after the localhost part, without much success. By accident I pasted it at the end as plain text, which resulted in this response:

![find_link](img/find_link.png)

I assumed that everything after the `#` will be treated as fragment and not as part of the path. Evidently, this assumption was wrong. I think I need to research a bit to find out where my train of thought went down the wrong way. Once I have a better understanding I'll update the description accordingly. But that is something for another day, for now finish the lab.

So adding a `/admin` to the end leads to the admin panel which shows the path to delete the user.

Now it is simply a copy and paste of the link to delete the user:

![delete_user](img/delete_user.png)

At the same time, the lab page updates to

![success](img/success.png)

# Write-up: Brute-forcing a stay-logged-in cookie @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Brute-forcing a stay-logged-in cookie* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

Learning path: Server-side topics → Authentication

Lab-Link: <https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Lab description

![lab_description](img/lab_description.png)

Clickable link for [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

## Steps

### Analyze cookie

As usual, the initial step is to analyze the login and 'stay-login' process. As such, I log in with the known credentials of the user `wiener`. In the response, a cookie is set that catches the eye:

![stay_logged_in_cookie](img/stay_logged_in_cookie.png)

Using Burp Suite, it immediately shows the decoded value in the Inspector:

![stay_logged_in_cookie_decoded](img/stay_logged_in_cookie_decoded.png)

It can be seen that the username is part of the cookie. If I can guess the second part correctly for a user it becomes possible to create valid cookies for that user.

![hash](img/hash.png)

The second part looks like a hash and is 32 characters long, which lets me think md5. Let's see if it is a simple md5 of the username (which would be a really fatal flaw as no password would be required) or the password (which would be not much better):

![md5_analysed](img/md5_analysed.png)

And indeed, the second part is an md5 hash of the password

### Brute force the cookie

I send the request of the account page to Burp Intruder, setting the `stay-logged-in` cookie as the payload

- Attack type: **Sniper**
- Payload: ![brute_force](img/brute_force.png)

For each of the passwords, I hash it, add the username in front and base64-encode everything. I also set on the options page a matching rule to quickly see if I am logged in as user `carlos`:

![matching rule](img/matching_rule.png)

And sure enough, ordering after this rule just has a single hit and the lab updates:

![brute_force_result](img/brute_force_result.png)

### Brute force the password

As the hash is not salted (does not contain any random part) it becomes easy to get the password with the help of [rainbow tables](https://en.wikipedia.org/wiki/Rainbow_table). As the candidate password file is rather short, the password brute force can be done quickly without them though:

![password_of_carlos](img/password_of_carlos.png)

And yes, I know that this approach is very bad in real life as it calculates every single hash before it does the grep, but it was the fastest to type that came into mind :)

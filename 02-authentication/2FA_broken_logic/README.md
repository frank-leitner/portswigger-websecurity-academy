# Lab: 2FA broken logic

Lab-Link: <https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Known information

- 2FA authentication is used, having flawed logic
- Credentials given for user `wiener:peter` + access to his 2FA emails
- Goals:
  - Access account page of user `carlos`

## Steps

### Analyse successful login process

We have access to a valid user account on that system, so login to see how the normal authentication flow looks like.

![login wiener credentials](img/login_wiener_credentials.png)

![login wiener 2fa](img/login_wiener_2fa.png)

On the website everything looks as expected. Next step is to analyse the requests and responses in more details:

![Response to login with credentials](img/login_response.png)

The first interesting thing is that the username provided in the POST request is reflected back as a cookie. In the request of the security code (`login2`), this cookie is included:

![username in cookie](img/username_in_cookie.png)

I wonder what happens if the cookie value gets replaced in the second step? In theory, it should not matter because everything should be combined into a session on the server side, never involving any client side storage of information for anything but the session ID.

### Modify cookies

Trying to repeat every request sent so far with just changing the `verify=wiener` to `verify=carlos` in the cookie did not result in anything useful yet. However, some of them might have triggered the setup of a 2FA code for `carlos`.

This lab allows to completely bypass the credentials check for the victim account, the only thing required is an own set of credentials and a valid username for the victim.

![login account carlos in intruder](img/fake_login_carlos.png)

- Attack type: **Sniper**
- Payload: Numbers, 0-9999, Number format 4 digits

![login account carlos in intruder, result](img/brute_forced_second_factor.png)

Now simply select `Request in browser` from the context menu to:

![success](img/success.png)

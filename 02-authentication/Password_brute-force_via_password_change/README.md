# Write-up: Password brute-force via password change @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Password brute-force via password change* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

Learning path: Server-side topics → Authentication

Lab-Link: <https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Lab description

![lab_description](img/lab_description.png)

Clickable link for [Candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords)

## Steps

### Analyze password change

As usual, the first step is to analyze the functionality of the lab, in this case, the password change feature. I log in as `wiener` with the known credentials and change the password.

The form contains a hidden field for the username:

![hidden_input](img/hidden_input.png)

Ideally, the web application should limit the password change to the session of the current user. But if this would be the case, the explicit inclusion of the username in the form would be redundant. Therefore I guess that the username may be taken from this client-side input.

### Brute force current password, naive attempt

I send the request to Burp Intruder:

![request payload](img/request_payload.png)

- Attack type: **Sniper**
- Payload: List of candidate passwords

The response to all requests looks identical:

![response](img/response.png)

When I changed the password for my own account, the result was a `200 OK`. My first guess is that after the current password is wrong during the password change, the system invalidates the current session. I try it out by changing the password of `wiener` but provide an incorrect current password. 

Sure enough, I receive a 302 to the login page and lost my session.

### Brute force current password, take 2

So before every password change attempt, I log in as `wiener` to provide a valid session and use it for one password guess.

To avoid that I have to do it manually all the time I create a macro that repeats the login and use it as a session rule. To be sure that the rule is applied I select `Include all ` URLs` as the session handling rule.

![macro](img/macro.png)

Now I repeat the naive attempt. This time, the result is very much different:

![password_changed](img/password_changed.png)

All that is left is logging in with `carlos:password` to get:

![success](img/success.png)

Of course, next time the real `carlos` wants to login, he will notice that his password does not work. In the best case scenario he'll just assume he forgot it and uses the `forgotten password` feature without thinking much about it. But it is very possible that he suspects foul play and catches something fishy is going on (which is bad for us as attacker).

So a much more subtle approach is to set the old password as the new password. This lowers the chance that the user notices this.

### An unexpected twist

While writing the script for this lab, I encountered a nice twist.

Brute forcing the password and changing it worked as expected, I got the `Password changed successfully!` message. But when I tried to login afterwards to verify that the lab is solved, I encountered the error `You have made too many incorrect login attempts. Please try again in 1 minute(s).`. Obviously, the invalid password guess attempts to change the password count for the brute force check during login. My manual solution was slow enough to not notice it, but python tries to verify too fast.

Nicely played, thank you!

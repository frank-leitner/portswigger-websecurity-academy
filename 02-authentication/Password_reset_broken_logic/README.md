# Write-up: Password reset broken logic @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Password reset broken logic* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

Learning path: Server-side topics → Authentication

Lab-Link: <https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)

## Lab description

![lab_description](img/lab_description.png)

## Steps

### Analyze

As usual, the first step is to analyze the functionality of the lab, in this case, the reset functionality. For this reset the password for `wiener`.

![reset_own_account_pw](img/reset_own_account_pw.png)

The request for the `forgot-password` feature does not look that much interesting. It contains a few headers that may be interesting, but nothing obvious. The body only contains the username.

![request_forgot_password](img/request_forgot_password.png)

It results in an email being sent to the email of wiener:

![email_wiener_reset](img/email_wiener_reset.png)

Clicking on the link allows me to enter a new password for `wiener`:

![new_password_wiener](img/new_password_wiener.png)

The corresponding POST request looks much more interesting, as it contains the username:

![POST_change_password_wiener](img/POST_change_password_wiener.png)

I wonder... if I request a new password as `wiener`, intercept this POST and change the username to `carlos`:

![POST_change_password_carlos](img/POST_change_password_carlos.png)

The request goes through as normal. I now try to log in with the credentials I just step, `carlos:password`, and voila:

![success](img/success.png)

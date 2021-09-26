# Lab: Password reset broken logic

Lab-Link: <https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic>  
Difficulty: APPRENTICE  
Python script: Currently no script

## Known information

- Vulnerable password reset functionality
- Known credential for user `wiener:peter`
- Access to emails of wiener is provided
- Goals:
  - Reset password of `carlos`
  - Access account page of `carlos`

## Steps

### Analyse

As usual, the first step is to analyse the reset functionality. For this reset the password for `wiener`.

![reset_own_account_pw](img/reset_own_account_pw.png)

The request of the `forgot-password` feature does not look that much interesting. It contains a few headers that may be interesting, but nothing obvious. The body only contains the username.

![request_forgot_password](img/request_forgot_password.png)

It results in an email being sent to the email of wiener:

![email_wiener_reset](img/email_wiener_reset.png)

Clicking on the link allows to enter a new password for `wiener`:

![new_password_wiener](img/new_password_wiener.png)

The corresponding POST request looks much more interesting, as it contains the username:

![POST_change_password_wiener](img/POST_change_password_wiener.png)

I wonder if I can request a new password as `wiener`, than intercept this POST and change the username to `carlos`:

![POST_change_password_carlos](img/POST_change_password_carlos.png)

Now try to login with `carlos:password` and voila:

![success](img/success.png)

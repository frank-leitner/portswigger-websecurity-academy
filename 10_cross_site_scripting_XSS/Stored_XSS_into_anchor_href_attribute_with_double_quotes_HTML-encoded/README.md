# Lab: Stored XSS into anchor href attribute with double quotes HTML-encoded

Lab-Link: <https://portswigger.net/web-security/cross-site-scripting/contexts/lab-href-attribute-double-quotes-html-encoded>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Known information

- Applications has a XSS vulnerability in the comment feature
- Goals:
  - Raise an `alert` box when the author name of a comment is clicked

## Steps

### The (currently) working but 'wrong' way

As usual, the first step is to analyse the application. As a test I post a comment with an HTML tag in all fields (except the email). It results in this HTML:

![html](img/html.png)

The name and comment fields escape the brackets, while the website does not. Therefore not all input is treated as equally malicious. Next is to find out what other characters may be allowed. As in the [last lab](../Reflected_XSS_into_attribute_with_angle_brackets_HTML-encoded/README.md), I use `xX';!--"<XSS>=&{()}Xx` as input in these fields:

![find_allowed_characters](img/find_allowed_characters.png)

This results in this interesting looking HTML code:

![escaped_attribute](img/escaped_attribute.png)

It shows clearly, that the double quote in the website URL terminates the string. So I can use it to inject other attributes or, as brackets are not encoded either, arbitrary other tags.

The lab states that the `alert` should be raised when the author name is clicked. So I inject `http://www.example.com" onclick="alert(document.domain)` as website to result in this HTML:

![injected_attribute](img/injected_attribute.png)

Clicking on the author name raises the expected `alert` box, confirming the XSS for the domain:

![alert](img/alert.png)

The lab updates to

![success](img/success.png)

(technically, the lab updates to 'solved' directly after sending the comment, not after clicking the link)

### And now the correct way

After seeing the 'solved' image above I realized that I did not read the lab name properly before. It seems that the double quotes should be HTML-encoded and not be usable here. As such I assume that escape of the href and injecting another attribute is not the intended solution here.

A way to inject the `alert` within the href attribute is to inject a JavaScript URL: `javascript:alert(document.domain)` as website. This results in this HTML which also solves the lab and is, I guess, the intended solution:

![correct_solution](img/correct_solution.png)

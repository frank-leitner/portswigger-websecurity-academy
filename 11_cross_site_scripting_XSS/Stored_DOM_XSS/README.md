# Lab: Stored DOM XSS

Lab-Link: <https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-stored>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Known information

- Application contains a stored DOM vulnerability in the comment function
- Goals:
  - Raise an `alert` box

## Steps

### Analysis

As usual, the first step is to analyse the website. A comment function is always a nice playground to try to do something not intended, as by its very definition it takes user provided content. If this content is not validated and sanitized properly, evil things may happen.

To I try the naive approach to inject things. I know it will not work (as there is another lab for this), but it will help me identify what may or may not be filtered.

So I post this comment:

![naive_comment](img/naive_comment.png)

and it results in this comment:

![safe_comment](img/safe_comment.png)

The more interesting part is the resulting HTML code though:

![naive_html](img/naive_html.png)

It shows that at least some countermeasures take place. What is interesting is that in both name and comment the first `<script>` tag was escaped, while the second one is suspiciously absent.

Trying to investigate a bit further, I send `x<b>X</b>x<b>X</b>x<b>X</b>x` as comment text, resulting in this HTML:

![bolded_comment](img/bolded_comment.png)

Looks like the first set of `<` and `>` is removed, the spurious `</b>` is ignored by the browser, all remaining tags go through unharmed. Looks like I found my avenue of attack, but out of interest I want to find out what is happening here.

The comments are not sent by the server directly with the response, but dynamically loaded and displayed via JavaScript:

![loading_comments](img/loading_comments.png)

So the natural next step is to check that JavaScript. Some things become obvious:

- The content of the elements are added as `innerHTML`, which is vulnerable to injections (`innerText` would be better here)
  ![innerHTML](img/innerHTML.png)
- The author of the code was vaguely aware of the dangers of using user provided input and tried to safeguard against it.
  ![escapeHTML](img/escapeHTML.png)
  The result, however, was less than ideal, as it simply replaces `<` and `>`
  
As I am only vaguely familiar with JavaScript, I check the [documentation of the string replace function](https://www.w3schools.com/jsref/jsref_replace.asp) and find this gem:

![replace_docu](img/replace_docu.png)

Why somebody may think this behaviour is a good idea is beyond me, but this confirms the guess above: only the first pair of `<>` is removed.

### Exploit, failed attempt

My first attempt is to use `<ignored><script>alert(document.domain)</script>` as payload. Unfortunately this does not work. It results in syntactically correct HTML/JavaScript:

![fail](img/fail.png)

But the script is not running. Taking a guess it may be because the code was already parsed by the JavaScript and called the `loadComments` script. Anything that this script adds to the page source is never visited by the parser as the JavaScript pass is finished already.

### Exploit

Therefore, next try is to add something that is native HTML like an `<img>` tag. Using the payload `<ignored><img src="xxx" onerror=alert(document.domain)>` finally results in the desired alert box confirming the vulnerability on the domain:

![alert](img/alert.png)

At the same moment, the lab updates to

![success](img/success.png)

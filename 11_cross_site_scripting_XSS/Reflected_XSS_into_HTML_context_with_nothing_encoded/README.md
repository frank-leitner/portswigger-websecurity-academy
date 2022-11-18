# Write-up: Reflected XSS into HTML context with nothing encoded @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Reflected XSS into HTML context with nothing encoded* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

**Learning path**: Client-side topics → Cross-site scripting

Lab-Link: <https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Lab description

![Lab description](img/lab_description.png)

## Steps

As usual, the first step is to analyze the application. In this case, it is the blog website with search functionality.

When searching for a term, it is reflected back in the result:

![search_term_in_result](img/search_term_in_result.png)

This behavior can cause issues if the search string is not sanitized correctly. 

I try by including simple HTML tags within my search input. These tags are embedded into the HTML source of the response without any escaping:

![HTML_in_response](img/HTML_in_response.png)

The most trivial XSS is to simply use `<script>` tags within the search term and hope that they, too, are embedded in the HTML:

![script_alert](img/script_alert.png)

Sure enough, this raises the alert box confirming the XSS vulnerability on the domain:

![alert_box](img/alert_box.png)

At the same time, the lab updates to

![success](img/success.png)

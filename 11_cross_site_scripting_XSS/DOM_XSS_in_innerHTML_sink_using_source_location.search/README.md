# Write-up: DOM XSS in innerHTML sink using source location.search @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *DOM XSS in innerHTML sink using source location.search* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

**Learning path**: Client-side topics → Cross-site scripting

Lab-Link: <https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Lab description

![Lab description](img/lab_description.png)

## Steps

The lab application is a blog website with search functionality. The search term is included on the result page. 

This is not performed on the server side, but by using client side JavaScript:

![HTML](img/HTML.png)

If the `search` argument is provided, the `innerHTML` of a `span`-element is changed dynamically. Inserting JavaScript by using `foo<img src="xxx" onerror=alert(document.domain)>` as search parameter results in this HTML:

![malicious_html](img/malicious_html.png)

This will raise the JavaScript `alert` box confirming the XSS vulnerability and updates the lab to

![success](img/success.png)

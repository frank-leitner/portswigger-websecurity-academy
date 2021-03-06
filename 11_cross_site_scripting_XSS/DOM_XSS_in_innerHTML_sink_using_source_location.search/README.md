# Lab: DOM XSS in innerHTML sink using source location.search

Lab-Link: <https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Known information

- Application contains a DOM-XSS vulnerability in the search feature
- Assigns user controlled input (`location.search`) to the `innerHTML` of an element
- Goals:
  - Raise an `alert` box

## Steps

When using the search in this lab application, the search term is displayed in the page. This is not performed on the server side, but by using client side JavaScript:

![HTML](img/HTML.png)

If the `search` argument is provided, the `innerHTML` of a `span`-element is changed dynamically. Inserting JavaScript by using `foo<img src="xxx" onerror=alert(document.domain)>` as search parameter results in this HTML:

![malicious_html](img/malicious_html.png)

This will raise the JavaScript `alert` box confirming the XSS vulnerability and updates the lab to

![success](img/success.png)

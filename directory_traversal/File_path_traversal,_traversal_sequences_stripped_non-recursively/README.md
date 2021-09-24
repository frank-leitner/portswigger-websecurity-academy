# Lab: File path traversal, traversal sequences stripped non-recursively

Lab-Link: <https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Known information

- Path traversal vulnerability in the product image display
- Path traversal sequences are removed by the application
- Goals:
  - Retrieve content of /etc/passwd

## Steps

### Analysis

The first step is as usual the analysis of the website. Like in the earlier labs on path traversal, the page references the product images as file names, indicating a possible path traversal vulnerability.

To improve handling of the path traversal, catch one of the image requests in Burp (ensure the filter does show image content) and send it to Repeater.

As described, using simple path traversal sequences like `../` does not lead to an actual path traversal. If the sequences are striped from the user input in a naive way, it removes all occurrances of `../` from the filename.

An input of `../../../etc/passwd` will therefore become the relative path `etc/passwd` which does not exist. Using `..//etc/passwd` in an attempt to create an absolute `/etc/passwd` does not find any file either.

But if just literal `../` sequences are removed, we simply need to provide a string that represents a path traversal string after the removal. Therefore `....//` will become `../` (the first two dots and the second slash remain after `../` is removed).

In order to obtain a result of `../../../etc/passwd`, we need to provide `....//....//....//etc/passwd`:

![request](img/request.png)

At the same time, the lab page updates to

![success](img/success.png)

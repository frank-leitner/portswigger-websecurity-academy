# Lab: OS command injection, simple case

Lab-Link: <https://portswigger.net/web-security/os-command-injection/lab-simple>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Known information

- OS command injection in the product stock checker
- Application executes shell command with product and store IDs, returns raw output
- Goals:
  - Execute `whoami`

## Steps

### Analysis

As usual, the first step is to browse around a bit. It is the usual showfront application known from previous labs. The new item here is the ability to check the availability of a product in different stores around the world:

![store_checker](img/store_checker.png)

Lets have a look how the request goes in Burp:

![store_checker_request](img/store_checker_request.png)

The request contains two parameter, productID and storeID, and returns a number as plain text in the response. Lets send the request to the repeater and see how it goes. As we have two parameter, I try to inject in both with different commands. This way, I can find out which parameter is injectable and in which order they are executed.

The script call might look something like this (likely not valid syntax, but the general idea is the same):

```php
echo system("someScript.sh $_REQUEST['productID'] $_REQUEST['storeId']")
```

The parameters are used as arguments for the script, its output is directly echoed back onto the HTML.

There are multiple ways to execute multiple commands in one line in a shell, separating the individual commands with for example `&`, `&&`, `|`, `||`, `;`. All behave slightly different. On Unix systems, my favourite is `;` as it completely separates the commands without side effects based on return conditions or execution order. In some conditions `&` is actually better as it backgrounds the command prior to my injection and runs my code without waiting for the other command to finish. Still, my favourite remains `;`.

SomeScript.sh might return a fail status without its arguments. We don't know the order of the arguments, and there might be more than just these two. Ideally, I want to just ignore the script completely and execute my injected command regardless.

Therefore I inject my command after a `;` in the POST parameters. (On a side note: when using `&`, it must be URLencoded).

![request_modified](img/request_modified.png)

From the response it can be seen that both parameters are injectable, and they are executed in the order productId first, storeId second.

### Solve the lab

What is missing now is just executing the `whoami` command to solve the lab. I comment out the remainder of the line after the `whoami` to avoid the error message of the second parameter:

![whoami](img/whoami.png)

And on a personal note, I like the stockreport script:

![script](img/script.png)

and the lab page updates to

![success](img/success.png)

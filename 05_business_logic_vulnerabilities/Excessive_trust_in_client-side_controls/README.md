# Write-up: Excessive trust in client-side controls @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Excessive trust in client-side controls* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

**Learning path**: Server-side topics → Business logic vulnerabilities

Lab-Link: <https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Lab description

![Lab description](img/lab_description.png)


## Steps

### Analysis

As usual, the first step is to check out the website. It is the usual shop website used in numerous labs already. Logging in with the known credentials I see that I have 100$ in store credit, which puts the jacket slightly out of the possible range

![A quite expensive jacket](img/oh_damn.png)

So what happens when I put it in the cart? It lands there, but placing the order brings the reality check - it is too expensive:

![Not enough money available](img/order_not_successful.png)

So have a look at the requests done so far in Burp. The request to add it to the card looks rather promising, as it contains the price as a parameter.

![Request to add an article](img/price_in_request.png)

---

### The malicious payload

Send that request to Repeater and change the price to something more reasonable. After all, it is just a leather jacket:

![Manipulated request containing a lower price tag](img/better_request.png)

Now, the looks much better already:

![The application uses the user-provided value](img/better_prices.png)

After placing the order, I still have a sizeable amount of store credit left:

![Order confirmation with manipulated price](img/order_confirmation.png)

At the same time, the lab updates to

![Lab solved](img/success.png)

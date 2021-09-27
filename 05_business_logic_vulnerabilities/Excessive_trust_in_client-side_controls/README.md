# Lab: Excessive trust in client-side controls

Lab-Link: <https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Known information

- Lab application does not adequately validates user input
- Price validation logic vulnerable
- Login credentials `wiener:peter`
- Goals:
  - Purchase a "Lightweight l33t leather jacket"

## Steps

### Analysis

As usual, the first step is to check out the website. It is the usual shop website used in numerous labs already. Logging in with the known credentials I see that I have 100$ in store credit, which puts the jacket slightly out of the possible range

![oh damn](img/oh_damn.png)

So what happens when I put it in the cart? It lands there, but placing the order brings the reality check - it is too expensive:

![order_not_successful](img/order_not_successful.png)

So have a look at the requests done so far in Burp. The request adding it to the card looks rather promising, as it contains the price as parameter.

![price_in_request](img/price_in_request.png)

### Exploit it

Send that request to Repeater and change the price to something more reasonable. After all, it is just a leather jacket:

![better_request](img/better_request.png)

Now, the looks much better already:

![better_prices](img/better_prices.png)

After placing the order, I still have a sizeable amount of store credit left, and the lab updates:

![success](img/success.png)

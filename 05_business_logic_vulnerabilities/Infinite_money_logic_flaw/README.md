# Write-up: Infinite money logic flaw @ PortSwigger Academy

![logo](img/logo.png)

This write-up for the lab *Infinite money logic flaw* is part of my walkthrough series for [PortSwigger's Web Security Academy](https://portswigger.net/web-security).

**Learning path**: Server-side topics → Business logic vulnerabilities

Lab-Link: <https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Lab description

![Lab description](img/lab_description.png)

## Steps

As usual, the first step is to analyze the functionality of the lab application. In this lab, it is a shop website well-known from other labs. My goal is to purchase a jacket that I already have a few thousand of. I start by browsing the page a bit and logging in with my known credentials.

The shop itself looks very familiar, but my account page has a new feature - I can use gift cards. Additionally, the lab provides access to my emails.

![account_page](img/account_page.png)

The gift cards can be purchased for \$10.

![gift_cards](img/gift_cards.png)

To find out how this works, simply buy one:

![gift_card_purchased](img/gift_card_purchased.png)

At the same time, I received an email, also containing the gift card code:

![gift_card_email](img/gift_card_email.png)

On the 'My account' website I can apply the gift card to bring my store credit back up to \$100. Unfortunately, I can not apply the gift card a second time. The gift card code can also not be used as a coupon on the checkout page.

![invalid_coupon](img/invalid_coupon.png)

Nothing obviously fishy comes up upon checking the requests in Burp.

---

### Subscribing to newsletter

The other option for interacting with the page is the newsletter. I subscribe to find out if there is any interesting reward for it:

![signup_discount](img/signup_discount.png)

It is a 30% discount. This makes me think... The gift card states \$10 flat rate value, can I apply the 30% on this? (after all, all shops I know in real life exclude gift cards explicitly from discounts)

![discount_on_gift_card](img/discount_on_gift_card.png)

At least it can be applied, so I buy it. After the code is generated and applied to my account, the store credit total shows \$3 higher than before:

![store_credit_after_applying_discounted_gift_card](img/store_credit_after_applying_discounted_gift_card.png)

So for \$7 I can purchase a \$10 gift card that redeems for face value.

---

### Purchasing gift cards

For the \$103 I have in store credit, I can purchase 14 gift cards, generating a \$3 profit each and a total of \$42

![purchasing_gift_cards](img/purchasing_gift_cards.png)

To obtain the \$1234 required to purchase the leather jacket, I need to redeem 412 gift cards. This is nothing I want to do manually, even though it could be a little less (<300) if I apply the 30% coupon for the jacket itself as well.

---

### Create a macro

The first thing is selecting the proper requests for a macro.

![select_requests_for_macro](img/select_requests_for_macro.png)

The POST to `/cart` does not contain a csrf-token, but the one to `/cart/coupon` does. So I modify the first request to `/cart` to redirect to `CART` so that the csrf-token for the next request can be extracted.

On the first test of the macro, redemption of the gift card failed as I forgot to change the gift card code to be taken from the previous request

![failed_redeem](img/failed_redeem.png)

So manually redeeming the code on the website to obtain my \$3, then changing the macro to obtain the value from the previous request:

![define_custom_parameter](img/define_custom_parameter.png)

And the request to redeem the gift card needs to be updated to actually use that value:

![updated_macro](img/updated_macro.png)

Now retest again

![macro_test_successful](img/macro_test_successful.png)

---

### Automate it

Now the macro test is successful, the parameter is obtained automatically and the gift card is applied. So I create a session rule that runs this macro for every request:

![session_rule](img/session_rule.png)

and send a plain request to `/my-account` to Burp Intruder. I clear all payload positions and add one for null payloads. During testing, I obtained already some of the 412 gift cards required, but use that number nonetheless as the number of payloads generated.

In addition, the requests must be made in order, so I use a resource pool with only a single concurrent request:

![resource_pool](img/resource_pool.png)

- Attack type: **Sniper**
- Payload: Null payload, 412 times

While the attack is running, refreshing of the account page in the browser shows a steady increase in store credit. So let it run for a while...

![enough_storecredit_for_purchase](img/purchase.png)

After it is finished, the cart looks much nicer for me and I can order. And I have no idea why I did not apply the discount code here, would have saved quite a number of calls.

![order_confirmation](img/confirmation.png)

At the same moment, the lab updates to

![success](img/success.png)

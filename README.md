# Write-up PortSwigger WebSecurity Academy

This repo contains my write-ups and scripts for solving the [PortSwigger WebSecurity Academy](https://portswigger.net/web-security). I plan to vaguely follow the learning path provided by PortSwigger, however, I expect to skip some of the expert-level labs initially.

If you find any problems with the descriptions or the scripts, feel free to open an [issue](https://github.com/frank-leitner/portswigger-websecurity-academy/issues) to help me improve the content of this repository.

I also post these write-ups and other content on medium.com. If you want to get notifications there, follow [my profile on medium](https://medium.com/@frank.leitner). 

## Goal

My ultimate goal is to obtain a level of expertise in the matter at hand to be able to pass the [Burp Suite Certified Practitioner](https://portswigger.net/web-security/certification) examination. As such, I not only want to solve the labs but also understand why the solution works.

The scripts are there to help me obtain some routine for creating such script files. Such a skill may not be that important to solve individual labs or the exam itself. But in real-life scenarios the ability to quickly create proofs-of-concept for vulnerabilities is helpful. 

So I create the scripts to learn about python and how to use it to interact with websites. Can these scripts be used to cheat the progress in the labs? Yes, but you only cheat yourself.

## Status

| ID | Topic | Apprentice | Practitioner | Expert | 
| --- | --- | :---: | :---: | :---: |
|    | **Server-side topics** ||||
| 01 | SQL injection | :heavy_check_mark: 2/2 | :heavy_multiplication_x: 14/15 | - |
| 02 | Authentication | :heavy_check_mark: 3/3 | :heavy_check_mark: 9/9 | :heavy_check_mark: 2/2 | 
| 03 | Directory traversal | :heavy_check_mark: 1/1 | :heavy_check_mark: 5/5 | - |
| 04 | Command inection | :heavy_check_mark: 1/1 | :heavy_check_mark: 4/4 | - |
| 05 | Business logic vulnerabilities | :heavy_check_mark: 4/4 | :heavy_multiplication_x: 6/7 | - |
| 06 | Information disclosure | :heavy_check_mark: 4/4 | :heavy_check_mark: 1/1 | - |
| 07 | Access control | :heavy_check_mark: 9/9 | :heavy_check_mark: 4/4 | - |
| 08 | File upload vulnerabilities | :heavy_check_mark: 2/2 | :heavy_check_mark: 4/4 | :heavy_multiplication_x: 0/1 |
| 09 | Server-side request forgery (SSRF) | :heavy_check_mark: 2/2 | :heavy_check_mark: 3/3 | :heavy_check_mark: 2/2 |
| 10 | XXE injection | :heavy_check_mark: 2/2 | :heavy_check_mark: 6/6 | :heavy_check_mark: 1/1|
|    | **Client-side topics** ||||
| 11 | Cross-site scripting (XSS) | :heavy_check_mark: 9/9 | :heavy_multiplication_x: 13/15 | :heavy_multiplication_x: 0/6 |
| 12 | Cross-site request forgery (CSRF) | :heavy_check_mark: 1/1 | :heavy_check_mark: 7/7 | - |
| 13 | Cross-origin resource sharing (CORS) | :heavy_check_mark: 2/2 | :heavy_check_mark: 1/1 | :heavy_multiplication_x: 0/1  |
| 14 | Clickjacking | :heavy_check_mark: 3/3 | :heavy_check_mark: 2/2 | - |
| 15 | DOM-based vulnerabilities | - | :heavy_check_mark: 5/5 | :heavy_multiplication_x: 0/2 |
| 16 | WebSockets | :heavy_check_mark: 1/1 | :heavy_check_mark: 2/2 | - |
|    | **Advanced topics** ||||
| 17 | Insecure deserialization | :heavy_check_mark: 1/1 | :heavy_multiplication_x: 5/6 | :heavy_multiplication_x: 0/3 |
| 18 | Server-side template injection | - | :heavy_multiplication_x: 2/5 | :heavy_multiplication_x: 0/2 |
| 19 | Web cache poisoning | - | :heavy_multiplication_x: 0/9 | :heavy_multiplication_x: 0/4 |
| 20 | HTTP Host header attacks | :heavy_check_mark: 2/2 | :heavy_multiplication_x: 0/4 | :heavy_multiplication_x: 0/1 |
| 21 | HTTP request smuggling | - | :heavy_multiplication_x: 1/15 | :heavy_multiplication_x: 0/7 |
| 22 | OAuth authentication | :heavy_check_mark: 1/1 | :heavy_multiplication_x: 1/4 | :heavy_multiplication_x: 0/1 |
| 23 | JWT attacks | :heavy_check_mark: 2/2 | :heavy_multiplication_x: 2/4 | :heavy_multiplication_x: 0/2 |
| 24 | Client-side prototype pollution | - | :heavy_multiplication_x: 0/5 | - |
| 25 | Essential skills | - | :heavy_multiplication_x: 0/1 | - |

Current status of script solutions:

![](img/script_solutions.png)

## Tooling

For the most part, I try to stick with using Burp Suite Pro and a browser only. I recommend using a cookie editor in the browser as well as a quick switch to using Burp Proxy.

Personally, I use [Cookie-Editor](https://cookie-editor.cgagnier.ca/) for manipulating cookies as well as [Proxy SwitchyOmega](https://github.com/FelisCatus/SwitchyOmega) to quickly (or even automatically) switch to Burp Proxy.

If you like to have the switching to proxy automated, you can setup a switch profile like this:

![switch_rules](img/switch_rules.png)

This way, all lab traffic automatically goes to Burp, while all other traffic gets the direct connection.

## Ressources

PortSwigger has very nice learning resources on their website. Basically, everything required to get started is there.

For a nice video series I can recommend the video series of [Rana Khalil](https://www.youtube.com/c/RanaKhalil101/playlists) on youtube. At the current time, she uploaded videos that cover SQL Injection and CSRF, but she shows everything she does and explains very nicely. And she uploads a new lab video each week (roughly), so I'm sure over time she will cover the full content of the WebSecurity Academy.

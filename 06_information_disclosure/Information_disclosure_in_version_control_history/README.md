# Lab: Information disclosure in version control history

Lab-Link: <https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-version-control-history>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py) NB: Not platform independent, works on Linux only (and perhaps on Mac). On Windows, it may run with WSL.

## Known information

- Lab discloses information in its version control history
- Goals:
  - Obtain administrator password
  - Delete user `carlos`

## Steps

### Analysis

The lab is again our favourite shop website. Browsing around does not reveal anything unusual. As we do not have known credentials, we need additional means of finding content.

This can be a wild guess based on the title, Burp's content discovery or any other directory search tool (e.g. gobuster, wfuzz, ...). Very quickly, it discovers an interesting directory:

![dirsearch_result](img/dirsearch_result.png)

I quickly mirror the directory with wget to create a local copy with the following line:

![download_git_directory](img/download_git_directory.png)

Checking the git log, an interesting commit message is shown in the last commit:

![git_log](img/git_log.png)

So go back to the commit before:

![get_old_commit](img/get_old_commit.png)

And check the content of the file:

![admin_password](img/admin_password.png)

Now it is simply a matter of logging in with `administrator:ehr6dyudul3bxk8n3prd`, access the `Admin panel` and delete user `carlos` to solve the lab:

![success](img/success.png)

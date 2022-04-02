# Lab: Remote code execution via web shell upload

Lab-Link: <https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-web-shell-upload>  
Difficulty: APPRENTICE  
Python script: [script.py](script.py)  

## Known information

- Applications contains vulnerable image upload
- No validations are performed on user input files
- Known good credentials: `wiener:peter`
- Goals:
  - Upload a PHP web shell
  - Exfiltrate `/home/carlos/secret` with this webshell

## Steps

### First look

The application is a blog website. In the public area nothing interesting appears obvious, so I proceed with the known user account of `wiener`. In the account settings, the user can set an email address as well as upload an avatar image:

![new_avatar](img/new_avatar.png)

### Find out what is allowed to upload

There might be a number of verification steps in place to check that the user provided input is not malicious (ignoring the fact that the lab description says there are no validations). Common types of validations are:

- File extension
- Content-type
- Mime type
- Signature (magic numbers, usually the first few bytes of a file, e.g. png uses `89 50 4E 47 0D 0A 1A 0A`)
- File parsing / rewriting

Most of these possible validations rely on information provided by the user. Therefore they can not be used reliably to validate the input. Unfortunately this does not stop a lot of web applications to rely on them.

So as a first step I need to find out what is allowed to upload. So try a simple text file. The application confirms the upload with

![uploaded_text_file](img/uploaded_text_file.png)

The HTML code of the page shows the URL for the (now broken) image as `/files/avatars/file.txt`. Browsing to this file shows my text file.

### Upload a web shell

In an ideal world, the website should not allow the upload of code files. It should also prevent any code that might end up in `/files/avatars/` to be executed. 

Considering this is an apprentice level lab, I try to upload a simple php file that calls a single shell command:

```php
<?php echo shell_exec('id'); ?>
```

The response is fairly clear, I'm allowed to execute shell commands:

![id_executed](img/id_executed.png)

So I send the original upload request into repeater and change the command to output the secret:

![upload_file_output](img/upload_file_output.png)

Calling the file will output the content of the secret file:

![secret_data](img/secret_data.png)

Submitting the information results in 

![success](img/success.png)

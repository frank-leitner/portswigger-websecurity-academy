# Lab: File path traversal, validation of file extension with null byte bypass

Lab-Link: <https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Known information

- Path traversal vulnerability in the product images
- Application ensures that provided path ends with the expected file extension
- Goals:
  - Retrieve content of /etc/passwd

## Steps

### Analysis

Like in the previous labs of the path traversal section, we start to analyse how the filenames for the images are provided. Here, the filenames are provided as basic filenames:

![html](img/html.png)

The rating image just below uses the `images` directory. Guessing that the product images might be in the same directory, try whether path traversal sequences are possible:

![request traversal](img/request_traversal.png)

And indeed, we can back out and return to the images directory. Now try the same with the `rating2.png` file:

![request_extension](img/request_extension.png)

This request does not provide the image. While we have of course no way of knowing that the two `images` directories are actually the same, it gives the indication that the file extension is checked (ignoring the fact that we know it due to the lab name).

This check may be done by simply comparing the last 4 characters of the filename with the string literal `.jpg`. Any type of such string comparisons may be vulnerable to an ancient issue: null termination of strings.

A lot of low level software like operating systems are written in C. In that language, strings are defined as sequences of characters that are followed by a null byte (a full byte all zeros in binary, or %00 in URLencoding). There was no way of checking the length of a string but iterating over it until a null byte was found.

As long as the null byte was found within the reserved memory area, the length of the string was found. For example, if within a 10 characters range the content is `ABCD%00`, than the string is `ABCD` with a length of 4. The amount of memory used is always one byte more than the usable length to account for the null byte.

This lead to a wonderful amout of bugs and vulnerabilities. If the developer does not account for this additional byte it can result in reading or writing over the reserved space, leading to all kind of undesired consequences, like application crashes (best case) or arbitrary code execution (best case for attackers).

A lot of low level functionality is still based on C, so terminates string at the first null byte found. If all components of a system agree on the same behaviour, this does not pose an issue (besides the inherent issues of null termination).

But if components treat strings differently, than this different behaviour can be exploited.

For example, a lot of more modern languages have dedicated string types and do neither require nor use null termination for their strings. In this case we want to access a file, so at some point the request will be passed from the application to the operating system

So we need to construct a string that fulfils these requirements:

- Succeeds the filename check in the application, in this case ending in `.jpg`
- Contains a null byte so that the operating system will not process the full filename
- Result filename must reference `/etc/passwd`

Above we already established that basic path traversal is possible. So a valid filename that fulfils the requirements would be `../../../etc/passwd%00DoesNotMatter.jpg`

So catch a image request in Burp and send it to Repeater:

![request passwd](img/request_passwd.png)

At this point, the lab page updates to

![success](img/success.png)

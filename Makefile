
test	:
	@echo token=$(TOKEN)
	./vaccine.py http://localhost:8080/vulnerabilities/sqli/index.php

test2	:
	./vaccine.py http://altoromutual.com/login.jsp -x post

test3	:
	./vaccine.py http://localhost:8000 -x post

setup	:
	-docker run -it -d -p 8080:80 vulnerables/web-dvwa
	-docker run -d -p 8000:80 gitlab.cylab.be:8081/cylab/play/sqlite-injection

fclean	:
	docker system prune

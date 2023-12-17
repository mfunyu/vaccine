all	:
	docker run -it -d -p 8080:80 vulnerables/web-dvwa
	docker run -d -p 8081:80 -p 5000:5000 -p 1080:1080 -e 'SeedingSettings:Admin=admin@ssrd.io' -e 'SeedingSettings:AdminPassword=admin' ssrd/securebank
	docker run -p 8000:80 gitlab.cylab.be:8081/cylab/play/sqlite-injection

test	:
	@echo token=$(TOKEN)
	./vaccine.py http://localhost:8080/vulnerabilities/sqli/index.php

test2	:
	./vaccine.py http://altoromutual.com/login.jsp -x post

test3	:
	-docker run -p 8000:80 gitlab.cylab.be:8081/cylab/play/sqlite-injection
	./vaccine.py http://localhost:8000 -x post 
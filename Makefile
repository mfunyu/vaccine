all	:
	docker run -it -d -p 8080:80 vulnerables/web-dvwa

test	:
	./vaccine.py http://altoromutual.com/login.jsp -x post

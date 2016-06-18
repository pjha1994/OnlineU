image:
	sudo docker build -t docker-onlineu .
container:
	docker run -p 80:80 docker-onlineu


image:
	sudo docker build -t docker-onlineu .
container:
	docker run -t -i -p 80:80 docker-onlineu
push-image:
	docker push jdsutton/docker-onlineu


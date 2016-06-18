image:
	sudo docker build -t jdsutton/onlineu:latest .
container:
	docker run -t -i -p 80:80 jdsutton/onlineu
push-image:
	docker push jdsutton/onlineu


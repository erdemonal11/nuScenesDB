IMAGE_NAME = nuscene
CONTAINER_NAME = nuscene-db
DOCKERFILE = Dockerfile.nuscene

include .env
export $(shell sed 's/=.*//' .env)

.PHONY: all
all: build run

.PHONY: build
build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .

.PHONY: run
run: stop
	docker run --network="host" -e DB_USER=erdem -e DB_PASSWORD=erdem -e DB_HOST=host.docker.internal -e DB_PORT=5432 -e DB_NAME=nuScene --name nuscene-db nuscene

.PHONY: stop
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

.PHONY: clean
clean: stop
	docker rmi $(IMAGE_NAME) || true

.PHONY: rebuild
rebuild: clean build run

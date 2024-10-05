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
	docker run --network="host" -e DB_USER=$(DB_USER) -e DB_PASSWORD=$(DB_PASSWORD) -e DB_HOST=$(DB_HOST) -e DB_PORT=$(DB_PORT) -e DB_NAME=$(DB_NAME) --name $(CONTAINER_NAME) $(IMAGE_NAME)

.PHONY: stop
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

.PHONY: clean
clean: stop
	docker rmi $(IMAGE_NAME) || true

.PHONY: rebuild
rebuild: clean build run

IMAGE_NAME = nuscene
CONTAINER_NAME = nuscene-db
DOCKERFILE = Dockerfile.nuscene

API_IMAGE = nuscene-api
API_CONTAINER = nuscene-api-container
API_DOCKERFILE = Dockerfile.api

include .env
export $(shell sed 's/=.*//' .env)

.PHONY: all
all: build run api-build api-run

.PHONY: build
build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .

.PHONY: run
run: stop
	docker run --network="host" \
		-e DB_USER=$(DB_USER) \
		-e DB_PASSWORD=$(DB_PASSWORD) \
		-e DB_HOST=host.docker.internal \
		-e DB_PORT=$(DB_PORT) \
		-e DB_NAME=$(DB_NAME) \
		-v $(SQL_FILE_PATH):/app/nuScene.sql \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

.PHONY: stop
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

.PHONY: clean
clean: stop
	docker rmi $(IMAGE_NAME) || true

.PHONY: rebuild
rebuild: clean build run

.PHONY: api-build
api-build:
	docker build -f $(API_DOCKERFILE) -t $(API_IMAGE) .

.PHONY: api-run
api-run: api-stop
	docker run --network="host" -e DB_USER=$(DB_USER) -e DB_PASSWORD=$(DB_PASSWORD) -e DB_HOST=$(DB_HOST) -e DB_PORT=$(DB_PORT) -e DB_NAME=$(DB_NAME) -e API_HOST=$(API_HOST) -e API_PORT=$(API_PORT) --name $(API_CONTAINER) $(API_IMAGE)

.PHONY: api-stop
api-stop:
	docker stop $(API_CONTAINER) || true
	docker rm $(API_CONTAINER) || true

.PHONY: api-clean
api-clean: api-stop
	docker rmi $(API_IMAGE) || true

.PHONY: api-rebuild
api-rebuild: api-clean api-build api-run

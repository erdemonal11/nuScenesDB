IMAGE_NAME = nuscene
CONTAINER_NAME = nuscene-db
DOCKERFILE = Dockerfile.nuscene

DB_INSERT_IMAGE = nuscene-dbinsert
DB_INSERT_CONTAINER = nuscene-insert-db
DB_INSERT_DOCKERFILE = Dockerfile.dbinsert

include .env
export $(shell sed 's/=.*//' .env)

.PHONY: all
all: build run dbinsert

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

.PHONY: dbinsert-build
dbinsert-build:
	docker build -f $(DB_INSERT_DOCKERFILE) -t $(DB_INSERT_IMAGE) .

.PHONY: dbinsert-run
dbinsert-run: dbinsert-stop
	docker run --network="host" -e DB_USER=$(DB_USER) -e DB_PASSWORD=$(DB_PASSWORD) -e DB_HOST=$(DB_HOST) -e DB_PORT=$(DB_PORT) -e DB_NAME=$(DB_NAME) --name $(DB_INSERT_CONTAINER) $(DB_INSERT_IMAGE) sh -c "until pg_isready -h $$DB_HOST -p $$DB_PORT; do echo waiting for database; sleep 2; done && python dbinsert.py"

.PHONY: dbinsert-stop
dbinsert-stop:
	docker stop $(DB_INSERT_CONTAINER) || true
	docker rm $(DB_INSERT_CONTAINER) || true

.PHONY: dbinsert-clean
dbinsert-clean: dbinsert-stop
	docker rmi $(DB_INSERT_IMAGE) || true

.PHONY: dbinsert-rebuild
dbinsert-rebuild: dbinsert-clean dbinsert-build dbinsert-run

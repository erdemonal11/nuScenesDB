# Include environment variables from .env file
include .env
export

# Create Docker network
.PHONY: network
network:
	docker network create $(DOCKER_NETWORK) || true

# Build DB image
.PHONY: build-db
build-db:
	docker build -t nuscene -f Dockerfile .

# Build API image
.PHONY: build-api
build-api:
	docker build -t nuscene-api -f Dockerfile.api .

# Run database container
.PHONY: run-db
run-db: network
	docker run --network=$(DOCKER_NETWORK) \
		--env-file .env \
		-e DB_HOST=host.docker.internal \
		-e SQL_FILE_PATH=/app/nuScene.sql \
		-v "$(PWD)/nuScene.sql:/app/nuScene.sql" \
		-v "$(NUSCENES_DATAROOT):$(NUSCENES_DATAROOT)" \
		--add-host=host.docker.internal:host-gateway \
		--name nuscene-db \
		nuscene

# Run API container
.PHONY: run-api
run-api: network
	docker run -d --network=$(DOCKER_NETWORK) \
		--env-file .env \
		-e DB_HOST=host.docker.internal \
		-e API_PORT=8000 \
		--add-host=host.docker.internal:host-gateway \
		-p 127.0.0.1:8000:8000 \
		--name nuscene-api \
		nuscene-api

# Stop and remove containers
.PHONY: clean
clean:
	docker stop nuscene-db nuscene-api || true
	docker rm nuscene-db nuscene-api || true

# Build and run everything
.PHONY: all
all: build-db build-api run-db run-api

# Stop everything and remove containers
.PHONY: down
down: clean
	docker network rm $(DOCKER_NETWORK) || true

# Check API status
.PHONY: check-api
check-api:
	@echo "Checking API container status..."
	@docker ps | grep nuscene-api || echo "API container is not running"
	@echo "\nAPI Logs:"
	@docker logs nuscene-api 2>&1 || echo "Cannot get API logs - container might not be running"

# Check DB status
.PHONY: check-db
check-db:
	@echo "Checking DB container status..."
	@docker ps | grep nuscene-db || echo "DB container is not running"
	@echo "\nDB Logs:"
	@docker logs nuscene-db 2>&1 || echo "Cannot get DB logs - container might not be running"

# Check all services
.PHONY: status
status:
	@echo "=== Service Status ==="
	@echo "\nDatabase:"
	@make -s check-db
	@echo "\nAPI:"
	@make -s check-api

# Build and run everything from scratch
.PHONY: start-fresh
start-fresh:
	@echo "Cleaning up old containers..."
	@make down
	@echo "\nBuilding images..."
	@make build-db
	@make build-api
	@echo "\nStarting services..."
	@make run-db
	@make run-api
	@echo "\nChecking status..."
	@make status

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make all          - Build and run everything"
	@echo "  make start-fresh  - Clean, rebuild, and start everything"
	@echo "  make down        - Stop and remove all containers"
	@echo "  make build-db    - Build database image"
	@echo "  make build-api   - Build API image"
	@echo "  make run-db      - Run database container"
	@echo "  make run-api     - Run API container"
	@echo "  make status      - Check status of all services"
	@echo "  make check-db    - Check database status and logs"
	@echo "  make check-api   - Check API status and logs"
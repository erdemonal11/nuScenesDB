# nuScenesDB 

This project contains a Python script that connects to a PostgreSQL database and executes a SQL script. The application is containerized using Docker, allowing for easy setup and execution using `Makefile` commands.

## Project Structure

- **`dbconnect.py`**: Python script that connects to a PostgreSQL database and runs a `.sql` file.
- **`Dockerfile.nuscene`**: Dockerfile for building the container image.
- **`nuScene.sql`**: SQL script containing the schema or queries to be executed.
- **`.env`**: Environment file storing database connection parameters.
- **`Makefile`**: File containing commands to build, run, stop, clean, and rebuild the Docker container.

## Prerequisites

- Docker installed and running on your machine.
- PostgreSQL server running and configured to accept external connections.
- Python 3.10 (only if you plan to run the script outside of Docker).

## Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd nuScenesDB
```

2. Create the **`.env`** File

```bash
DB_HOST=192.168.0.3
DB_PORT=5432
DB_NAME=nuScene
DB_USER=your_username
DB_PASSWORD=your_password
```

## Build and Run with Makefile

The `Makefile` provides several commands to manage the Docker container.

### 1. Build the Docker Image

```bash
make build
```

This command will start the container and execute the **`dbconnect.py`** script.

### 2. Run the Container

```bash
make run
```

### 3. Stop the Container

```bash
make stop
```

### 4. Remove the Docker Image

```bash
make clean
```

### 5. Rebuild and Run the Container

```bash
make rebuild
```

## Notes

- Ensure that your PostgreSQL server is configured to allow connections from the Docker container by modifying `postgresql.conf` and `pg_hba.conf`.
- The `Makefile` uses environment variables stored in the `.env` file for the database connection.
- If you encounter any issues with container name conflicts, use the `make stop` command to stop and remove existing containers before rerunning.


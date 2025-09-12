# Advanced CQRS Application - Docker Setup

This is a Spring Boot application implementing CQRS (Command Query Responsibility Segregation) architecture, containerized with Docker.

## Architecture

The application uses:
- **PostgreSQL** for the command side (write operations)
- **MongoDB** for the query side (read operations)  
- **Spring Boot** as the main framework
- **Port 8087** for the web application

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository** (if not already done)

2. **Navigate to the project directory:**
   ```bash
   cd /home/crwy/Documents/Academic/Universidad/8\ Semestre/Microservicios/CQRS/arquitectura-software-udemy/cqrs/advanced-cqrs
   ```

3. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Application: http://localhost:8087
   - PostgreSQL: localhost:10001
   - MongoDB: localhost:10002

## Available Services

### Application Endpoints
- Command Controller: `http://localhost:8087/api/command/*`
- Query Controller: `http://localhost:8087/api/query/*`
- Sync Controller: `http://localhost:8087/api/sync/*`

### Database Access
- **PostgreSQL**: 
  - Host: localhost
  - Port: 10001
  - Database: postgres
  - Username: postgres
  - Password: postgres
  - Schema: cqrs

- **MongoDB**:
  - Host: localhost
  - Port: 10002
  - Database: admin
  - Username: mongo
  - Password: mongo

## Docker Commands

### Start services in background:
```bash
docker-compose up -d
```

### Stop services:
```bash
docker-compose down
```

### Rebuild and restart:
```bash
docker-compose down
docker-compose up --build
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f mongodb
```

### Remove volumes (clean database):
```bash
docker-compose down -v
```

## Development

To make changes to the application:

1. Modify the source code
2. Rebuild the container:
   ```bash
   docker-compose up --build app
   ```

## Port Configuration

The application runs on port **8087** by default. To change it:

1. Update the `SERVER_PORT` environment variable in `docker-compose.yml`
2. Update the port mapping in the `app` service
3. Rebuild and restart the containers

## Troubleshooting

### Database Connection Issues
- Make sure all containers are running: `docker-compose ps`
- Check logs: `docker-compose logs -f`
- Verify database containers are healthy

### Port Conflicts
If port 8087 is already in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:8087"
```

### Clean Start
For a completely clean environment:
```bash
docker-compose down -v
docker system prune -f
docker-compose up --build
```

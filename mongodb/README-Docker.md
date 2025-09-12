# CQRS MongoDB Application - Docker

Esta aplicación Spring Boot ha sido dockerizada para ejecutarse con una base de datos MongoDB.

## Configuración

- **Puerto de la aplicación**: 8085
- **Puerto de MongoDB**: 27017
- **Base de datos**: cqrs_db

## Ejecutar la aplicación

### Opción 1: Con docker-compose (recomendado)

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en background
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener los servicios
docker-compose down

# Detener y eliminar volúmenes (elimina datos de la BD)
docker-compose down -v
```

### Opción 2: Manualmente con Docker

```bash
# Crear una red
docker network create cqrs-network

# Ejecutar MongoDB
docker run -d \
  --name cqrs-mongodb \
  --network cqrs-network \
  -p 27017:27017 \
  -e MONGO_INITDB_DATABASE=cqrs_db \
  mongo:5.0

# Construir la aplicación
docker build -t cqrs-app .

# Ejecutar la aplicación
docker run -d \
  --name cqrs-app \
  --network cqrs-network \
  -p 8085:8085 \
  -e SPRING_PROFILES_ACTIVE=docker \
  cqrs-app
```

## Acceso a la aplicación

Una vez que los contenedores estén ejecutándose, puedes acceder a:

- **Aplicación**: http://localhost:8085
- **MongoDB**: localhost:27017

## Verificación

Para verificar que todo está funcionando correctamente:

```bash
# Verificar que los contenedores están ejecutándose
docker-compose ps

# Verificar logs de la aplicación
docker-compose logs app

# Verificar logs de MongoDB
docker-compose logs mongodb
```

## Comandos útiles

```bash
# Reconstruir solo la aplicación
docker-compose build app

# Reiniciar un servicio específico
docker-compose restart app

# Acceder al contenedor de la aplicación
docker-compose exec app bash

# Acceder a MongoDB
docker-compose exec mongodb mongo cqrs_db
```

# CQRS PostgreSQL con Docker

Esta aplicación implementa el patrón CQRS (Command Query Responsibility Segregation) con PostgreSQL y incluye un script de migración Flyway que inserta 1 millón de registros.

## 🚀 Inicio Rápido

### Prerequisitos
- Docker
- Docker Compose

### Ejecución
```bash
# Opción 1: Script automático
./run-docker.sh

# Opción 2: Comandos manuales
docker-compose up --build -d
```

## 📊 Datos Generados

El script de migración `V2_0__Insert_Million_Records.sql` crea:
- **100,000 posts** con contenido generado
- **500,000 comentarios** (5 por cada post)
- **~400,000 reacciones** (cantidad variable aleatoria)
- **Total: ~1,000,000 registros**

## 🌐 Servicios Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| API Spring Boot | http://localhost:5100 | API REST principal |
| Adminer | http://localhost:8081 | Administrador de base de datos |
| PostgreSQL | localhost:5432 | Base de datos (puerto externo) |

## 🗄️ Acceso a la Base de Datos

### Via Adminer (Recomendado)
1. Ir a http://localhost:8081
2. **Sistema**: PostgreSQL
3. **Servidor**: postgres
4. **Usuario**: postgres
5. **Contraseña**: postgres
6. **Base de datos**: postgres

### Via Cliente PostgreSQL
```bash
psql -h localhost -p 5432 -U postgres -d postgres
```

## 📋 Comandos Útiles

```bash
# Ver logs de la aplicación
docker-compose logs cqrs-app

# Ver logs de PostgreSQL
docker-compose logs postgres

# Conectar a la base de datos
docker-compose exec postgres psql -U postgres

# Parar todos los servicios
docker-compose down

# Parar y limpiar volúmenes
docker-compose down --volumes

# Reconstruir solo la aplicación
docker-compose up --build cqrs-app
```

## 🔍 Verificar Inserciones

Una vez que la aplicación esté ejecutándose, puedes verificar los datos:

```sql
-- Contar registros por tabla
SELECT 'posts' as table_name, COUNT(*) as count FROM cqrs.post
UNION ALL
SELECT 'comments', COUNT(*) FROM cqrs.comment
UNION ALL
SELECT 'reactions', COUNT(*) FROM cqrs.comment_reaction;

-- Ver algunos ejemplos
SELECT p.id, p.content, COUNT(c.id) as comment_count 
FROM cqrs.post p 
LEFT JOIN cqrs.comment c ON p.id = c.post_id 
GROUP BY p.id 
LIMIT 10;
```

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker        │    │   Spring Boot   │    │   PostgreSQL    │
│   Container     │────│   Application   │────│   Database      │
│   (App)         │    │   (CQRS)        │    │   (Data)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │     Flyway      │
                       │   (Migrations)  │
                       └─────────────────┘
```

## ⚙️ Configuración

### Variables de Entorno
- `SPRING_DATASOURCE_URL`: URL de conexión a PostgreSQL
- `SPRING_DATASOURCE_USERNAME`: Usuario de base de datos
- `SPRING_DATASOURCE_PASSWORD`: Contraseña de base de datos
- `SPRING_FLYWAY_ENABLED`: Habilitar migraciones Flyway

### Perfiles de Spring
- **Desarrollo local**: `application.properties`
- **Docker**: `application-docker.properties`

## 🚨 Solución de Problemas

### La aplicación no se conecta a la base de datos
- Verificar que PostgreSQL esté saludable: `docker-compose ps`
- Ver logs: `docker-compose logs postgres`

### Las migraciones no se ejecutan
- Verificar logs de Flyway: `docker-compose logs cqrs-app`
- Conectar a la DB y verificar tabla `flyway_schema_history`

### Rendimiento lento durante inserciones
- El script está optimizado para PostgreSQL
- Las inserciones pueden tomar varios minutos en sistemas con recursos limitados
- Monitorear recursos: `docker stats`

## 📈 Monitoreo

```bash
# Ver recursos utilizados
docker stats

# Ver espacio en disco
docker system df

# Ver logs en tiempo real
docker-compose logs -f cqrs-app
```

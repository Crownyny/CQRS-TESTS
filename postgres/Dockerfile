# Dockerfile para la aplicación Spring Boot
FROM openjdk:17-jdk-slim

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración Maven
COPY pom.xml .
COPY mvnw .
COPY mvnw.cmd .
COPY .mvn .mvn

# Copiar código fuente
COPY src ./src

# Dar permisos de ejecución al script Maven
RUN chmod +x ./mvnw

# Construir la aplicación (esto también ejecutará las pruebas)
RUN ./mvnw clean package -DskipTests

# Exponer el puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["java", "-jar", "target/cqrs-postgres-0.0.1-SNAPSHOT.jar"]

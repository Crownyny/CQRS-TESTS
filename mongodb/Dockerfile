# Usar una imagen base más estable de Eclipse Temurin
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# Copiar archivos de Maven
COPY pom.xml .
COPY mvnw .
COPY mvnw.cmd .
COPY .mvn .mvn

# Hacer ejecutable el wrapper de Maven
RUN chmod +x mvnw

# Descargar dependencias
RUN ./mvnw dependency:go-offline -B

# Copiar código fuente
COPY src ./src

# Construir la aplicación
RUN ./mvnw clean package -DskipTests

# Exponer el puerto
EXPOSE 8085

# Comando para ejecutar la aplicación
CMD ["java", "-jar", "target/cqrs-mongo-0.0.1-SNAPSHOT.jar"]

#!/bin/bash

# Script para ejecutar la aplicación CQRS con Docker
# Este script facilita el levantamiento completo del stack

echo "🚀 Iniciando aplicación CQRS con PostgreSQL..."
echo "================================================"

# Limpiar contenedores previos si existen
echo "🧹 Limpiando contenedores anteriores..."
docker-compose down --volumes --remove-orphans

# Construir e iniciar los servicios
echo "🔨 Construyendo y iniciando servicios..."
docker-compose up --build -d

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 10

# Mostrar logs de la aplicación
echo "📋 Mostrando logs de la aplicación..."
echo "================================================"
docker-compose logs -f cqrs-app

# Función para mostrar información útil cuando se interrumpe
trap 'echo ""; echo "🛑 Interrumpido por el usuario"; echo "📝 Para ver logs: docker-compose logs cqrs-app"; echo "🗄️  Para acceder a la DB: http://localhost:8081 (adminer)"; echo "🌐 API disponible en: http://localhost:5100"; echo "🛑 Para parar: docker-compose down"; exit 0' INT

echo "✅ Aplicación lista!"
echo "📝 Logs en tiempo real (Ctrl+C para salir)"
echo "🗄️  Adminer (DB): http://localhost:8081"
echo "🌐 API: http://localhost:5100"

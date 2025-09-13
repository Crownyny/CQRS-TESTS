-- Script de inicialización de la base de datos
-- Este script se ejecuta automáticamente cuando se crea el contenedor de PostgreSQL

-- Crear el esquema cqrs si no existe
CREATE SCHEMA IF NOT EXISTS cqrs;

-- Configuraciones para mejorar el rendimiento durante las inserciones masivas
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Recargar la configuración
SELECT pg_reload_conf();

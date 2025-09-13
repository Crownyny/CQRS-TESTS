#!/usr/bin/env python3
"""
Script de prueba de rendimiento para MongoDB
Realiza 50 inserciones y 50 consultas, midiendo el tiempo de cada operación
Genera un archivo CSV con los resultados y un archivo TXT con estadísticas
"""

import time
import csv
import statistics
import random
import string
from pymongo import MongoClient
from datetime import datetime

# Configuración de conexión a MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "cqrs_db"
COLLECTION_NAME = "posts"

def generate_random_post(index):
    """Genera un post aleatorio para insertar"""
    words = ["tecnología", "innovación", "desarrollo", "software", "base de datos", 
             "rendimiento", "optimización", "escalabilidad", "arquitectura", "microservicios",
             "MongoDB", "Spring Boot", "Java", "aplicación", "sistema"]
    
    content_words = random.sample(words, random.randint(10, 15))
    content = " ".join(content_words)
    
    return {
        "_id": f"test_post_{index}_{int(time.time())}_{random.randint(1000, 9999)}",
        "content": f"Post de prueba número {index} - {content}",
        "createdAt": datetime.now(),
        "comments": []
    }

def run_performance_test():
    """Ejecuta el test de rendimiento completo"""
    print("Conectando a MongoDB...")
    
    # Conexión a MongoDB
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Verificar conexión
        client.server_info()
        print(f"Conectado exitosamente a {DATABASE_NAME}")
        
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return
    
    insert_times = []
    query_times = []
    inserted_ids = []
    
    print("\n=== INICIANDO TEST DE RENDIMIENTO ===")
    print(f"Timestamp: {datetime.now()}")
    
    # Fase 1: 50 Inserciones
    print("\n--- FASE 1: INSERCIONES ---")
    for i in range(50):
        post = generate_random_post(i + 1)
        
        start_time = time.time()
        collection.insert_one(post)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        insert_times.append(duration_ms)
        inserted_ids.append(post["_id"])
        
        print(f"Inserción {i+1:2d}: {duration_ms:6.2f} ms")
    
    # Fase 2: 50 Consultas
    print("\n--- FASE 2: CONSULTAS ---")
    for i in range(50):
        # Consultar un documento aleatorio de los insertados
        random_id = random.choice(inserted_ids)
        
        start_time = time.time()
        result = collection.find_one({"_id": random_id})
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        query_times.append(duration_ms)
        
        print(f"Consulta {i+1:2d}: {duration_ms:6.2f} ms")
    
    # Generar archivos de resultados
    print("\n--- GENERANDO ARCHIVOS DE RESULTADOS ---")
    generate_csv_file(insert_times, query_times)
    generate_stats_file(insert_times, query_times)
    
    # Limpiar datos de prueba
    print("\n--- LIMPIANDO DATOS DE PRUEBA ---")
    delete_result = collection.delete_many({"_id": {"$in": inserted_ids}})
    print(f"Eliminados {delete_result.deleted_count} documentos de prueba")
    
    client.close()
    print("\n=== TEST COMPLETADO ===")

def generate_csv_file(insert_times, query_times):
    """Genera archivo CSV con los resultados"""
    filename = f"performance_results_{int(time.time())}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Operacion', 'Numero', 'Tiempo_ms'])
        
        # Escribir tiempos de inserción
        for i, time_ms in enumerate(insert_times, 1):
            writer.writerow(['INSERT', i, f"{time_ms:.2f}"])
        
        # Escribir tiempos de consulta
        for i, time_ms in enumerate(query_times, 1):
            writer.writerow(['SELECT', i, f"{time_ms:.2f}"])
    
    print(f"Archivo CSV generado: {filename}")

def generate_stats_file(insert_times, query_times):
    """Genera archivo TXT con estadísticas"""
    filename = f"performance_stats_{int(time.time())}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("ESTADÍSTICAS DE RENDIMIENTO MONGODB\n")
        f.write("=" * 50 + "\n")
        f.write(f"Fecha y hora: {datetime.now()}\n")
        f.write(f"Total de operaciones: {len(insert_times) + len(query_times)}\n\n")
        
        # Estadísticas de inserción
        f.write("OPERACIONES DE INSERCIÓN:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Número de operaciones: {len(insert_times)}\n")
        f.write(f"Tiempo promedio: {statistics.mean(insert_times):.2f} ms\n")
        f.write(f"Desviación estándar: {statistics.stdev(insert_times):.2f} ms\n")
        f.write(f"Tiempo mínimo: {min(insert_times):.2f} ms\n")
        f.write(f"Tiempo máximo: {max(insert_times):.2f} ms\n")
        f.write(f"Mediana: {statistics.median(insert_times):.2f} ms\n")
        f.write(f"Tiempo total: {sum(insert_times):.2f} ms\n\n")
        
        # Estadísticas de consulta
        f.write("OPERACIONES DE CONSULTA:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Número de operaciones: {len(query_times)}\n")
        f.write(f"Tiempo promedio: {statistics.mean(query_times):.2f} ms\n")
        f.write(f"Desviación estándar: {statistics.stdev(query_times):.2f} ms\n")
        f.write(f"Tiempo mínimo: {min(query_times):.2f} ms\n")
        f.write(f"Tiempo máximo: {max(query_times):.2f} ms\n")
        f.write(f"Mediana: {statistics.median(query_times):.2f} ms\n")
        f.write(f"Tiempo total: {sum(query_times):.2f} ms\n\n")
        
        # Estadísticas generales
        all_times = insert_times + query_times
        f.write("ESTADÍSTICAS GENERALES:\n")
        f.write("-" * 21 + "\n")
        f.write(f"Total de operaciones: {len(all_times)}\n")
        f.write(f"Tiempo promedio general: {statistics.mean(all_times):.2f} ms\n")
        f.write(f"Desviación estándar general: {statistics.stdev(all_times):.2f} ms\n")
        f.write(f"Tiempo total del test: {sum(all_times):.2f} ms\n")
        
        # Percentiles
        f.write(f"Percentil 50 (mediana): {statistics.median(all_times):.2f} ms\n")
        f.write(f"Percentil 90: {statistics.quantiles(all_times, n=10)[8]:.2f} ms\n")
        f.write(f"Percentil 95: {statistics.quantiles(all_times, n=20)[18]:.2f} ms\n")
        f.write(f"Percentil 99: {statistics.quantiles(all_times, n=100)[98]:.2f} ms\n")
        
        # Comparación entre operaciones
        f.write(f"\nCOMPARACIÓN:\n")
        f.write("-" * 12 + "\n")
        insert_avg = statistics.mean(insert_times)
        query_avg = statistics.mean(query_times)
        
        if insert_avg > query_avg:
            diff = insert_avg - query_avg
            f.write(f"Las inserciones son {diff:.2f} ms más lentas que las consultas en promedio\n")
        else:
            diff = query_avg - insert_avg
            f.write(f"Las consultas son {diff:.2f} ms más lentas que las inserciones en promedio\n")
    
    print(f"Archivo de estadísticas generado: {filename}")

if __name__ == "__main__":
    print("Script de prueba de rendimiento MongoDB")
    print("Asegúrate de que MongoDB esté ejecutándose en localhost:27017")
    
    try:
        run_performance_test()
    except KeyboardInterrupt:
        print("\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"Error durante el test: {e}")

client = MongoClient("mongodb://localhost:27017/")
db = client["cqrs_db"]
collection = db["posts"]

try:
    count = collection.count_documents({})
    print(f"Total de documentos en la colección 'posts': {count:,}")
    
    # También puedes ver estadísticas adicionales
    stats = db.command("collStats", "posts")
    print(f"Tamaño de la colección: {stats.get('size', 0):,} bytes")
    print(f"Número de índices: {stats.get('nindexes', 0)}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
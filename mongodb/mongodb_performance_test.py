#!/usr/bin/env python3
"""
Script de prueba de rendimiento para API REST (MongoController en localhost:8085)
Realiza 50 inserciones de posts y 50 consultas, midiendo el tiempo de cada operación
Genera un archivo CSV con los resultados y un archivo TXT con estadísticas
"""

import time
import csv
import statistics
import random
import requests
from datetime import datetime

# Configuración de conexión a la API
BASE_URL = "http://localhost:8085"

def generate_random_post(index):
    """Genera un post aleatorio para insertar"""
    words = ["tecnología", "innovación", "desarrollo", "software", "base de datos", 
             "rendimiento", "optimización", "escalabilidad", "arquitectura", "microservicios",
             "MongoDB", "Spring Boot", "Java", "aplicación", "sistema"]
    
    content_words = random.sample(words, random.randint(10, 15))
    content = " ".join(content_words)

    return {
        "id": f"test_post_{index}_{int(time.time())}_{random.randint(1000, 9999)}",
        "title": f"Post de prueba número {index}",
        "content": content
    }

def run_performance_test():
    """Ejecuta el test de rendimiento completo"""
    insert_times = []
    query_times = []
    inserted_ids = []
    
    print("\n=== INICIANDO TEST DE RENDIMIENTO API ===")
    print(f"Timestamp: {datetime.now()}")
    
    # Fase 1: 50 Inserciones
    print("\n--- FASE 1: INSERCIONES ---")
    for i in range(50):
        post = generate_random_post(i + 1)
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/post", json=post)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        insert_times.append(duration_ms)

        if response.status_code == 200:
            inserted_ids.append(post["id"])
        else:
            print(f"Error en inserción {i+1}: {response.status_code} {response.text}")
        
        print(f"Inserción {i+1:2d}: {duration_ms:6.2f} ms")
    
    # Fase 2: 50 Consultas
    print("\n--- FASE 2: CONSULTAS ---")
    for i in range(50):
        if not inserted_ids:
            break

        random_id = random.choice(inserted_ids)
        
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/post/{random_id}")
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        query_times.append(duration_ms)

        if response.status_code != 200:
            print(f"Error en consulta {i+1}: {response.status_code} {response.text}")
        
        print(f"Consulta {i+1:2d}: {duration_ms:6.2f} ms")
    
    # Generar archivos de resultados
    print("\n--- GENERANDO ARCHIVOS DE RESULTADOS ---")
    generate_csv_file(insert_times, query_times)
    generate_stats_file(insert_times, query_times)
    
    print("\n=== TEST COMPLETADO ===")

def generate_csv_file(insert_times, query_times):
    """Genera archivo CSV con los resultados"""
    filename = f"performance_results_{int(time.time())}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Operacion', 'Numero', 'Tiempo_ms'])
        
        for i, time_ms in enumerate(insert_times, 1):
            writer.writerow(['INSERT', i, f"{time_ms:.2f}"])
        
        for i, time_ms in enumerate(query_times, 1):
            writer.writerow(['SELECT', i, f"{time_ms:.2f}"])
    
    print(f"Archivo CSV generado: {filename}")

def generate_stats_file(insert_times, query_times):
    """Genera archivo TXT con estadísticas"""
    filename = f"performance_stats_{int(time.time())}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("ESTADÍSTICAS DE RENDIMIENTO API\n")
        f.write("=" * 50 + "\n")
        f.write(f"Fecha y hora: {datetime.now()}\n")
        f.write(f"Total de operaciones: {len(insert_times) + len(query_times)}\n\n")
        
        # Inserciones
        if insert_times:
            f.write("OPERACIONES DE INSERCIÓN:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Número de operaciones: {len(insert_times)}\n")
            f.write(f"Tiempo promedio: {statistics.mean(insert_times):.2f} ms\n")
            f.write(f"Tiempo mínimo: {min(insert_times):.2f} ms\n")
            f.write(f"Tiempo máximo: {max(insert_times):.2f} ms\n\n")
        
        # Consultas
        if query_times:
            f.write("OPERACIONES DE CONSULTA:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Número de operaciones: {len(query_times)}\n")
            f.write(f"Tiempo promedio: {statistics.mean(query_times):.2f} ms\n")
            f.write(f"Tiempo mínimo: {min(query_times):.2f} ms\n")
            f.write(f"Tiempo máximo: {max(query_times):.2f} ms\n\n")
        
        all_times = insert_times + query_times
        if all_times:
            f.write("ESTADÍSTICAS GENERALES:\n")
            f.write("-" * 21 + "\n")
            f.write(f"Total de operaciones: {len(all_times)}\n")
            f.write(f"Tiempo promedio general: {statistics.mean(all_times):.2f} ms\n")
            f.write(f"Tiempo total del test: {sum(all_times):.2f} ms\n")
    
    print(f"Archivo de estadísticas generado: {filename}")

if __name__ == "__main__":
    print("Script de prueba de rendimiento API (localhost:8085)")
    try:
        run_performance_test()
    except KeyboardInterrupt:
        print("\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"Error durante el test: {e}")

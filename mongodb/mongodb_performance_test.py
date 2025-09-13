#!/usr/bin/env python3
"""
Script de prueba de rendimiento para API REST (MongoController en localhost:8085)
Realiza 50 inserciones de reacciones (usando post+comment+reaction) y 50 consultas,
midiendo el tiempo de cada operación.
Genera un archivo CSV con los resultados y un archivo TXT con estadísticas.
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
    """Genera un post aleatorio"""
    return {
        "id": f"post_{index}_{int(time.time())}_{random.randint(1000,9999)}",
        "title": f"Post de prueba {index}",
        "content": f"Contenido aleatorio del post {index}"
    }

def generate_random_comment(index):
    """Genera un comentario aleatorio"""
    return {
        "id": f"comment_{index}_{int(time.time())}_{random.randint(1000,9999)}",
        "author": f"Autor{index}",
        "content": f"Comentario de prueba {index}"
    }

def generate_random_reaction(index):
    """Genera una reacción aleatoria"""
    reaction_types = ["LIKE", "LOVE", "HAHA", "WOW", "SAD", "ANGRY"]
    return {
        "id": f"reaction_{index}_{int(time.time())}_{random.randint(1000,9999)}",
        "type": random.choice(reaction_types),
        "user": f"user{random.randint(1,100)}"
    }

def run_performance_test():
    insert_times = []
    query_times = []
    reaction_refs = []  # Lista de (postId, commentId, reactionId)

    print("\n=== INICIANDO TEST DE RENDIMIENTO API ===")
    print(f"Timestamp: {datetime.now()}")

    # Fase 1: 50 Inserciones (sobre addReaction)
    print("\n--- FASE 1: INSERCIONES DE REACCIONES ---")
    for i in range(50):
        # Crear post
        post = generate_random_post(i+1)
        r_post = requests.post(f"{BASE_URL}/post", json=post)
        if r_post.status_code != 200:
            print(f"Error creando post {i+1}: {r_post.status_code}")
            continue

        # Crear comentario
        comment = generate_random_comment(i+1)
        r_comment = requests.post(f"{BASE_URL}/post/{post['id']}/comment", json=comment)
        if r_comment.status_code != 200:
            print(f"Error creando comentario {i+1}: {r_comment.status_code}")
            continue

        # Crear reacción (esta es la operación medida)
        reaction = generate_random_reaction(i+1)
        start_time = time.time()
        r_reaction = requests.post(
            f"{BASE_URL}/post/{post['id']}/comment/{comment['id']}/reaction",
            json=reaction
        )
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000
        insert_times.append(duration_ms)

        if r_reaction.status_code == 200:
            reaction_refs.append((post["id"], comment["id"], reaction["id"]))
        else:
            print(f"Error creando reacción {i+1}: {r_reaction.status_code} {r_reaction.text}")

        print(f"Inserción {i+1:2d}: {duration_ms:6.2f} ms")

    # Fase 2: 50 Consultas (sobre getPost)
    print("\n--- FASE 2: CONSULTAS DE POSTS ---")
    for i in range(50):
        if not reaction_refs:
            break

        postId, _, _ = random.choice(reaction_refs)

        start_time = time.time()
        r_get = requests.get(f"{BASE_URL}/post/{postId}")
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000
        query_times.append(duration_ms)

        if r_get.status_code != 200:
            print(f"Error consultando post {postId}: {r_get.status_code} {r_get.text}")

        print(f"Consulta {i+1:2d}: {duration_ms:6.2f} ms")

    # Resultados
    print("\n--- GENERANDO ARCHIVOS DE RESULTADOS ---")
    generate_csv_file(insert_times, query_times)
    generate_stats_file(insert_times, query_times)

    print("\n=== TEST COMPLETADO ===")

def generate_csv_file(insert_times, query_times):
    filename = f"performance_results_{int(time.time())}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Operacion', 'Numero', 'Tiempo_ms'])
        for i, t in enumerate(insert_times, 1):
            writer.writerow(['INSERT_REACTION', i, f"{t:.2f}"])
        for i, t in enumerate(query_times, 1):
            writer.writerow(['SELECT_POST', i, f"{t:.2f}"])
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
    print("Script de prueba de rendimiento API (usando addReaction)")
    try:
        run_performance_test()
    except KeyboardInterrupt:
        print("\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"Error durante el test: {e}")

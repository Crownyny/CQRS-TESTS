#!/usr/bin/env python3
"""
Script de prueba de rendimiento para aplicación CQRS
Realiza 50 inserciones y 50 consultas HTTP, midiendo el tiempo de cada operación
Genera un archivo CSV con los resultados y un archivo TXT con estadísticas
"""

import time
import csv
import statistics
import random
import string
import requests
import json
from datetime import datetime

# Configuración de conexión a la API
API_BASE_URL = "http://localhost:8087"
NUM_OPERATIONS = 50

def generate_random_post(index):
    """Genera un post aleatorio para insertar"""
    words = ["tecnología", "innovación", "desarrollo", "software", "base de datos", 
             "rendimiento", "optimización", "escalabilidad", "arquitectura", "microservicios",
             "MongoDB", "Spring Boot", "Java", "aplicación", "sistema", "CQRS", "performance"]
    
    content_words = random.sample(words, random.randint(8, 12))
    content = " ".join(content_words)
    
    return {
        "content": f"Post de prueba número {index} - {content} - {random.randint(1000, 9999)}"
    }

def check_server_connection():
    """Verifica que el servidor esté disponible"""
    print("Verificando conexión con el servidor...")
    
    try:
        # Intentar conectarse al servidor
        response = requests.get(f"{API_BASE_URL}", timeout=5)
        print(f"✓ Servidor responde en {API_BASE_URL}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ No se puede conectar al servidor: {e}")
        print("Asegúrate de que la aplicación esté ejecutándose en puerto 8087")
        return False

def test_endpoint_availability():
    """Prueba la disponibilidad de los endpoints"""
    print("\nProbando endpoints disponibles...")
    
    endpoints = [
        ("/actuator/health", "GET"),
        ("/post", "POST"),
        ("/post/1", "GET"),
        ("/sync", "POST")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            else:
                test_data = {"content": "test"} if "post" in endpoint else {}
                response = requests.post(f"{API_BASE_URL}{endpoint}", 
                                       json=test_data,
                                       headers={"Content-Type": "application/json"},
                                       timeout=5)
            
            print(f"  {method} {endpoint}: {response.status_code}")
            
            # Mostrar detalles del error para códigos problemáticos
            if response.status_code >= 400:
                error_text = response.text.strip()
                if error_text:
                    # Mostrar solo las primeras líneas del error
                    error_lines = error_text.split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"    → {line.strip()[:100]}...")
                            break
                
        except requests.exceptions.RequestException as e:
            print(f"  {method} {endpoint}: Error - {str(e)[:50]}...")

def perform_post_insertion(post_data, operation_number, endpoint="/post"):
    """Realiza una inserción de post y retorna el resultado"""
    start_time = time.time()
    success = False
    post_id = None
    status_code = None
    error_message = ""
    
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=post_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        status_code = response.status_code
        
        if response.status_code == 200 or response.status_code == 201:
            success = True
            try:
                response_data = response.json()
                post_id = response_data.get('id') or response_data.get('postId') or response_data.get('_id')
            except (json.JSONDecodeError, AttributeError):
                # Si no hay JSON válido, aún consideramos exitosa la operación si el status es 200/201
                post_id = f"post_{operation_number}_{int(time.time())}"
        else:
            error_message = response.text[:100] if response.text else f"HTTP {status_code}"
            
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        status_code = -1
        error_message = str(e)[:100]
    
    return {
        'duration_ms': duration_ms,
        'success': success,
        'post_id': post_id,
        'status_code': status_code,
        'error_message': error_message
    }

def perform_post_query(post_id, operation_number, endpoint="/post"):
    """Realiza una consulta de post y retorna el resultado"""
    start_time = time.time()
    success = False
    status_code = None
    error_message = ""
    
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}/{post_id}",
            timeout=10
        )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        status_code = response.status_code
        
        if response.status_code == 200:
            success = True
        else:
            error_message = response.text[:100] if response.text else f"HTTP {status_code}"
            
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        status_code = -1
        error_message = str(e)[:100]
    
    return {
        'duration_ms': duration_ms,
        'success': success,
        'status_code': status_code,
        'error_message': error_message
    }

def perform_sync_operation():
    """Realiza la sincronización entre PostgreSQL y MongoDB"""
    start_time = time.time()
    success = False
    status_code = None
    error_message = ""
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/sync",
            headers={"Content-Type": "application/json"},
            timeout=30  # Timeout más largo para sincronización
        )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        status_code = response.status_code
        
        if response.status_code == 200:
            success = True
        else:
            error_message = response.text[:100] if response.text else f"HTTP {status_code}"
            
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        status_code = -1
        error_message = str(e)[:100]
    
    return {
        'duration_ms': duration_ms,
        'success': success,
        'status_code': status_code,
        'error_message': error_message
    }

def run_performance_test():
    """Ejecuta el test de rendimiento completo"""
    if not check_server_connection():
        return
    
    test_endpoint_availability()
    working_endpoints = test_alternative_endpoints()
    
    # Determinar qué endpoints usar basándose en los que funcionan
    post_endpoint = "/post"  # Default
    query_endpoint = "/post"  # Default
    
    for endpoint, method in working_endpoints:
        if method == "POST" and ("post" in endpoint.lower() or "command" in endpoint.lower()):
            post_endpoint = endpoint
            print(f"✓ Usando endpoint de inserción: POST {endpoint}")
            break
    
    for endpoint, method in working_endpoints:
        if method == "GET" and ("post" in endpoint.lower() or "query" in endpoint.lower()):
            # Remover el ID del endpoint para usarlo como base
            query_endpoint = endpoint.replace("/1", "")
            print(f"✓ Usando endpoint de consulta: GET {query_endpoint}/{{id}}")
            break
    
    insert_times = []
    query_times = []
    inserted_post_ids = []
    test_results = []
    
    print(f"\n=== INICIANDO TEST DE RENDIMIENTO API ===")
    print(f"URL: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    print(f"Operaciones por tipo: {NUM_OPERATIONS}")
    
    # Fase 1: Inserciones
    print(f"\n--- FASE 1: INSERCIONES ({NUM_OPERATIONS} operaciones) ---")
    successful_inserts = 0
    
    for i in range(NUM_OPERATIONS):
        post_data = generate_random_post(i + 1)
        result = perform_post_insertion(post_data, i + 1, post_endpoint)
        
        insert_times.append(result['duration_ms'])
        
        # Guardar resultado completo
        test_results.append({
            'operation_type': 'INSERT',
            'operation_number': i + 1,
            'duration_ms': result['duration_ms'],
            'success': result['success'],
            'status_code': result['status_code'],
            'post_id': result['post_id'],
            'error_message': result['error_message']
        })
        
        if result['success']:
            successful_inserts += 1
            if result['post_id']:
                inserted_post_ids.append(result['post_id'])
            
        status_symbol = "✓" if result['success'] else "✗"
        print(f"Inserción {i+1:2d}: {result['duration_ms']:6.2f} ms - {status_symbol}")
        
        # Mostrar detalles del error en las primeras 3 inserciones fallidas
        if not result['success'] and i < 3 and result['error_message']:
            print(f"    Error: {result['error_message'][:80]}...")
    
    print(f"Inserciones exitosas: {successful_inserts}/{NUM_OPERATIONS} ({successful_inserts/NUM_OPERATIONS*100:.1f}%)")
    
    # Fase 2: Consultas
    print(f"\n--- FASE 2: CONSULTAS ({NUM_OPERATIONS} operaciones) ---")
    successful_queries = 0
    
    # Obtener IDs válidos de MongoDB después de la sincronización
    available_mongo_ids = get_available_post_ids()
    print(f"IDs disponibles en MongoDB: {len(available_mongo_ids)}")
    
    for i in range(NUM_OPERATIONS):
        # Usar IDs de MongoDB si están disponibles, sino usar IDs aleatorios
        if available_mongo_ids:
            post_id = random.choice(available_mongo_ids)
        elif inserted_post_ids:
            # Convertir Long ID a String (esto puede no funcionar ya que MongoDB usa ObjectId)
            post_id = str(random.choice(inserted_post_ids))
        else:
            # ID aleatorio como último recurso
            post_id = f"{random.randint(1, 1000)}"
        
        result = perform_post_query(post_id, i + 1, query_endpoint)
        
        query_times.append(result['duration_ms'])
        
        # Guardar resultado completo
        test_results.append({
            'operation_type': 'QUERY',
            'operation_number': i + 1,
            'duration_ms': result['duration_ms'],
            'success': result['success'],
            'status_code': result['status_code'],
            'post_id': post_id,
            'error_message': result['error_message']
        })
        
        if result['success']:
            successful_queries += 1
            
        status_symbol = "✓" if result['success'] else "✗"
        print(f"Consulta {i+1:2d} (ID {post_id}): {result['duration_ms']:6.2f} ms - {status_symbol}")
        
        # Mostrar detalles del error en las primeras 3 consultas fallidas
        if not result['success'] and i < 3 and result['error_message']:
            print(f"    Error: {result['error_message'][:80]}...")
    
    print(f"Consultas exitosas: {successful_queries}/{NUM_OPERATIONS} ({successful_queries/NUM_OPERATIONS*100:.1f}%)")
    
    # Generar archivos de resultados
    print("\n--- SINCRONIZANDO DATOS ---")
    sync_result = perform_sync_operation()
    if sync_result['success']:
        print("✓ Sincronización exitosa")
    else:
        print(f"✗ Error en sincronización: {sync_result['error_message']}")
    
    print("\n--- GENERANDO ARCHIVOS DE RESULTADOS ---")
    csv_filename = generate_csv_file(test_results)
    stats_filename = generate_stats_file(insert_times, query_times, successful_inserts, successful_queries)
    
    # Mostrar resumen final
    print_summary(insert_times, query_times, successful_inserts, successful_queries, test_results)
    
    print(f"\n=== TEST COMPLETADO ===")
    print(f"📁 Resultados guardados en: {csv_filename}")
    print(f"📊 Estadísticas guardadas en: {stats_filename}")

def generate_csv_file(test_results):
    """Genera archivo CSV con los resultados detallados"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_results_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['operation_type', 'operation_number', 'duration_ms', 'success', 
                     'status_code', 'post_id', 'error_message', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in test_results:
            result['timestamp'] = datetime.now().isoformat()
            writer.writerow(result)
    
    print(f"Archivo CSV generado: {filename}")
    return filename

def generate_stats_file(insert_times, query_times, successful_inserts, successful_queries):
    """Genera archivo TXT con estadísticas"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_statistics_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ESTADÍSTICAS DE RENDIMIENTO - APLICACIÓN CQRS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Fecha y hora: {datetime.now()}\n")
        f.write(f"URL base: {API_BASE_URL}\n")
        f.write(f"Operaciones por tipo: {NUM_OPERATIONS}\n\n")
        
        # Estadísticas de inserción
        f.write("OPERACIONES DE INSERCIÓN:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Número total de operaciones: {len(insert_times)}\n")
        f.write(f"Operaciones exitosas: {successful_inserts} ({successful_inserts/len(insert_times)*100:.1f}%)\n")
        f.write(f"Tiempo promedio: {statistics.mean(insert_times):.2f} ms\n")
        f.write(f"Desviación estándar: {statistics.stdev(insert_times):.2f} ms\n")
        f.write(f"Tiempo mínimo: {min(insert_times):.2f} ms\n")
        f.write(f"Tiempo máximo: {max(insert_times):.2f} ms\n")
        f.write(f"Mediana: {statistics.median(insert_times):.2f} ms\n")
        f.write(f"Tiempo total: {sum(insert_times):.2f} ms\n\n")
        
        # Estadísticas de consulta
        f.write("OPERACIONES DE CONSULTA:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Número total de operaciones: {len(query_times)}\n")
        f.write(f"Operaciones exitosas: {successful_queries} ({successful_queries/len(query_times)*100:.1f}%)\n")
        f.write(f"Tiempo promedio: {statistics.mean(query_times):.2f} ms\n")
        f.write(f"Desviación estándar: {statistics.stdev(query_times):.2f} ms\n")
        f.write(f"Tiempo mínimo: {min(query_times):.2f} ms\n")
        f.write(f"Tiempo máximo: {max(query_times):.2f} ms\n")
        f.write(f"Mediana: {statistics.median(query_times):.2f} ms\n")
        f.write(f"Tiempo total: {sum(query_times):.2f} ms\n\n")
        
        # Estadísticas generales
        all_times = insert_times + query_times
        total_successful = successful_inserts + successful_queries
        total_operations = len(all_times)
        
        f.write("ESTADÍSTICAS GENERALES:\n")
        f.write("-" * 21 + "\n")
        f.write(f"Total de operaciones: {total_operations}\n")
        f.write(f"Operaciones exitosas: {total_successful} ({total_successful/total_operations*100:.1f}%)\n")
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
        
        f.write(f"Tasa de éxito inserciones: {successful_inserts/len(insert_times)*100:.1f}%\n")
        f.write(f"Tasa de éxito consultas: {successful_queries/len(query_times)*100:.1f}%\n")
    
    print(f"Archivo de estadísticas generado: {filename}")
    return filename

def print_summary(insert_times, query_times, successful_inserts, successful_queries, test_results):
    """Imprime un resumen de los resultados en consola"""
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    total_operations = len(insert_times) + len(query_times)
    total_successful = successful_inserts + successful_queries
    
    print(f"📊 GENERAL:")
    print(f"  Total de operaciones: {total_operations}")
    print(f"  Operaciones exitosas: {total_successful} ({total_successful/total_operations*100:.1f}%)")
    
    print(f"\n📝 INSERCIONES:")
    print(f"  Total: {len(insert_times)}")
    print(f"  Exitosas: {successful_inserts} ({successful_inserts/len(insert_times)*100:.1f}%)")
    print(f"  Tiempo promedio: {statistics.mean(insert_times):.2f} ms")
    print(f"  Tiempo mediano: {statistics.median(insert_times):.2f} ms")
    
    print(f"\n🔍 CONSULTAS:")
    print(f"  Total: {len(query_times)}")
    print(f"  Exitosas: {successful_queries} ({successful_queries/len(query_times)*100:.1f}%)")
    print(f"  Tiempo promedio: {statistics.mean(query_times):.2f} ms")
    print(f"  Tiempo mediano: {statistics.median(query_times):.2f} ms")
    
    # Mostrar errores más comunes si los hay
    failed_operations = [r for r in test_results if not r['success']]
    if failed_operations:
        print(f"\n⚠️  ERRORES DETECTADOS ({len(failed_operations)} operaciones fallidas):")
        
        # Contar errores por código de estado
        error_counts = {}
        for op in failed_operations:
            code = op['status_code']
            if code not in error_counts:
                error_counts[code] = {'count': 0, 'example': op['error_message'][:50]}
            error_counts[code]['count'] += 1
        
        for code, info in error_counts.items():
            print(f"  Status {code}: {info['count']} ocurrencias")
            if info['example']:
                print(f"    Ejemplo: {info['example']}...")

def test_alternative_endpoints():
    """Prueba endpoints alternativos comunes en aplicaciones Spring Boot"""
    print("\nProbando endpoints alternativos...")
    
    alternative_endpoints = [
        # Posibles variaciones de endpoints para posts
        ("/api/post", "POST"),
        ("/api/posts", "POST"),
        ("/command/post", "POST"),
        ("/posts", "POST"),
        
        # Posibles endpoints de consulta
        ("/api/post/1", "GET"),
        ("/api/posts/1", "GET"),
        ("/query/post/1", "GET"),
        ("/posts/1", "GET"),
        
        # Endpoints de información
        ("/info", "GET"),
        ("/health", "GET"),
        ("/", "GET")
    ]
    
    working_endpoints = []
    
    for endpoint, method in alternative_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=3)
            else:
                test_data = {"content": "test endpoint"}
                response = requests.post(f"{API_BASE_URL}{endpoint}", 
                                       json=test_data,
                                       headers={"Content-Type": "application/json"},
                                       timeout=3)
            
            if response.status_code < 500:  # No es error interno del servidor
                status_msg = "✓" if response.status_code < 400 else "⚠"
                print(f"  {status_msg} {method} {endpoint}: {response.status_code}")
                
                if response.status_code < 400:
                    working_endpoints.append((endpoint, method))
                    
        except requests.exceptions.RequestException:
            pass  # Ignorar errores de conexión para endpoints que no existen
    
    if working_endpoints:
        print(f"\n✅ Endpoints que funcionan correctamente:")
        for endpoint, method in working_endpoints:
            print(f"  {method} {endpoint}")
    else:
        print("\n❌ No se encontraron endpoints que funcionen correctamente")
    
    return working_endpoints

def get_available_post_ids():
    """Obtiene los IDs de posts disponibles en MongoDB"""
    try:
        response = requests.get(f"{API_BASE_URL}/posts", timeout=10)
        
        if response.status_code == 200:
            posts = response.json()
            if posts and isinstance(posts, list):
                return [post['id'] for post in posts if 'id' in post]
        
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo IDs de posts: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Script de Prueba de Rendimiento - Aplicación CQRS")
    print("=" * 60)
    print("Este script realiza pruebas de rendimiento contra la API REST")
    print(f"URL base configurada: {API_BASE_URL}")
    print(f"Operaciones por tipo: {NUM_OPERATIONS}")
    print("=" * 60)
    
    try:
        run_performance_test()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        print("\nSugerencias:")
        print("- Verificar que la aplicación esté ejecutándose: docker-compose up -d")
        print("- Revisar los logs: docker-compose logs -f app")
        print("- Verificar que las bases de datos estén activas")

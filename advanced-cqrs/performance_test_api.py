#!/usr/bin/env python3
"""
Script de pruebas de rendimiento para aplicación CQRS
Inserciones siguen el flujo:
  Post → Comment → Reaction (se mide principalmente el endpoint de Reaction)
"""

import requests
import time
import csv
import statistics
from datetime import datetime
import random
import string

# Configuración
API_BASE_URL = "http://localhost:8085"
NUM_OPERATIONS = 50

class PerformanceTest:
    def __init__(self):
        self.results = []
        self.post_ids = []

    def generate_random_content(self, length=50):
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))

    def test_reaction_insertion(self, operation_number):
        start_time = time.perf_counter()
        success = False
        post_id, status_code, error_message = None, None, ""

        try:
            # 1. Crear Post
            post_data = {"content": self.generate_random_content()}
            post_resp = requests.post(f"{API_BASE_URL}/post", json=post_data, timeout=10)
            post_id = post_resp.json().get("id")
            self.post_ids.append(post_id)

            # 2. Crear Comment
            comment_data = {"author": "Tester", "content": self.generate_random_content(20)}
            comment_resp = requests.post(f"{API_BASE_URL}/post/{post_id}/comment", json=comment_data, timeout=10)
            comment_id = comment_resp.json().get("id")

            # 3. Crear Reaction
            reaction_data = {"type": random.choice(["LIKE", "LOVE", "HAHA", "WOW"]), "user": f"user_{operation_number}"}
            reaction_resp = requests.post(f"{API_BASE_URL}/post/{post_id}/comment/{comment_id}/reaction", json=reaction_data, timeout=10)

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            status_code = reaction_resp.status_code
            success = reaction_resp.status_code in (200, 201)

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            status_code = -1
            error_message = str(e)[:100]

        return {
            'operation_type': 'INSERT',
            'operation_number': operation_number,
            'duration_ms': duration_ms,
            'success': success,
            'status_code': status_code,
            'post_id': post_id,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        }

    def test_post_query(self, post_id, operation_number):
        start_time = time.perf_counter()
        success, status_code, error_message = False, None, ""

        try:
            response = requests.get(f"{API_BASE_URL}/post/{post_id}", timeout=10)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            status_code = response.status_code
            success = response.status_code == 200

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            status_code = -1
            error_message = str(e)[:100]

        return {
            'operation_type': 'QUERY',
            'operation_number': operation_number,
            'duration_ms': duration_ms,
            'success': success,
            'status_code': status_code,
            'post_id': post_id,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        }

    def run_insertion_tests(self):
        print(f"Ejecutando {NUM_OPERATIONS} pruebas de inserción (Reaction)...")
        for i in range(NUM_OPERATIONS):
            result = self.test_reaction_insertion(i + 1)
            self.results.append(result)
            print(f"  Inserción {i+1}: {result['duration_ms']:.2f}ms - {'✓' if result['success'] else '✗'}")
            time.sleep(0.1)


    def run_query_tests(self):
        print(f"\nEjecutando {NUM_OPERATIONS} pruebas de consulta (Post)...")
        available_ids = self.post_ids.copy()

        for i in range(NUM_OPERATIONS):
            post_id = random.choice(available_ids) if available_ids else str(random.randint(1, 1000))
            result = self.test_post_query(post_id, i + 1)
            self.results.append(result)
            print(f"  Consulta {i+1} (ID {post_id}): {result['duration_ms']:.2f}ms - {'✓' if result['success'] else '✗'}")
            time.sleep(0.1)

            
    def save_csv_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_results_{timestamp}.csv"
        fieldnames = ['operation_type', 'operation_number', 'duration_ms', 'success',
                      'status_code', 'post_id', 'error_message', 'timestamp']
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        return filename

    def calculate_and_save_statistics(self):
        insert_times = [r['duration_ms'] for r in self.results if r['operation_type'] == 'INSERT' and r['success']]
        query_times = [r['duration_ms'] for r in self.results if r['operation_type'] == 'QUERY' and r['success']]
        all_times = insert_times + query_times

        insert_success = len(insert_times)
        query_success = len(query_times)
        insert_total = NUM_OPERATIONS
        query_total = NUM_OPERATIONS

        def safe_stats(times):
            if not times:
                return None
            return {
                "avg": statistics.mean(times),
                "stdev": statistics.pstdev(times) if len(times) > 1 else 0.0,
                "min": min(times),
                "max": max(times),
                "median": statistics.median(times),
                "total": sum(times),
                "p90": statistics.quantiles(times, n=100)[89] if len(times) > 1 else times[0],
                "p95": statistics.quantiles(times, n=100)[94] if len(times) > 1 else times[0],
                "p99": statistics.quantiles(times, n=100)[98] if len(times) > 1 else times[0],
            }

        insert_stats = safe_stats(insert_times)
        query_stats = safe_stats(query_times)
        all_stats = safe_stats(all_times)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_statistics_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ESTADÍSTICAS DE RENDIMIENTO - APLICACIÓN CQRS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Fecha y hora: {datetime.now()}\n")
            f.write(f"URL base: {API_BASE_URL}\n")
            f.write(f"Operaciones por tipo: {NUM_OPERATIONS}\n\n")

            # Inserciones
            f.write("OPERACIONES DE INSERCIÓN:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Número total de operaciones: {insert_total}\n")
            f.write(f"Operaciones exitosas: {insert_success} ({insert_success/insert_total*100:.1f}%)\n")
            if insert_stats:
                f.write(f"Tiempo promedio: {insert_stats['avg']:.2f} ms\n")
                f.write(f"Desviación estándar: {insert_stats['stdev']:.2f} ms\n")
                f.write(f"Tiempo mínimo: {insert_stats['min']:.2f} ms\n")
                f.write(f"Tiempo máximo: {insert_stats['max']:.2f} ms\n")
                f.write(f"Mediana: {insert_stats['median']:.2f} ms\n")
                f.write(f"Tiempo total: {insert_stats['total']:.2f} ms\n\n")

            # Consultas
            f.write("OPERACIONES DE CONSULTA:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Número total de operaciones: {query_total}\n")
            f.write(f"Operaciones exitosas: {query_success} ({query_success/query_total*100:.1f}%)\n")
            if query_stats:
                f.write(f"Tiempo promedio: {query_stats['avg']:.2f} ms\n")
                f.write(f"Desviación estándar: {query_stats['stdev']:.2f} ms\n")
                f.write(f"Tiempo mínimo: {query_stats['min']:.2f} ms\n")
                f.write(f"Tiempo máximo: {query_stats['max']:.2f} ms\n")
                f.write(f"Mediana: {query_stats['median']:.2f} ms\n")
                f.write(f"Tiempo total: {query_stats['total']:.2f} ms\n\n")

            # Generales
            f.write("ESTADÍSTICAS GENERALES:\n")
            f.write("-" * 21 + "\n")
            f.write(f"Total de operaciones: {insert_total + query_total}\n")
            f.write(f"Operaciones exitosas: {insert_success + query_success} ({(insert_success+query_success)/(insert_total+query_total)*100:.1f}%)\n")
            if all_stats:
                f.write(f"Tiempo promedio general: {all_stats['avg']:.2f} ms\n")
                f.write(f"Desviación estándar general: {all_stats['stdev']:.2f} ms\n")
                f.write(f"Tiempo total del test: {all_stats['total']:.2f} ms\n")
                f.write(f"Percentil 50 (mediana): {all_stats['median']:.2f} ms\n")
                f.write(f"Percentil 90: {all_stats['p90']:.2f} ms\n")
                f.write(f"Percentil 95: {all_stats['p95']:.2f} ms\n")
                f.write(f"Percentil 99: {all_stats['p99']:.2f} ms\n\n")

            # Comparación
            f.write("COMPARACIÓN:\n")
            f.write("-" * 12 + "\n")
            if insert_stats and query_stats:
                diff = insert_stats['avg'] - query_stats['avg']
                f.write(f"Las inserciones son {abs(diff):.2f} ms más {'lentas' if diff > 0 else 'rápidas'} que las consultas en promedio\n")
            f.write(f"Tasa de éxito inserciones: {insert_success/insert_total*100:.1f}%\n")
            f.write(f"Tasa de éxito consultas: {query_success/query_total*100:.1f}%\n")

        return filename

def main():
    test = PerformanceTest()
    test.run_insertion_tests()
    test.run_query_tests()
    csv_file = test.save_csv_results()
    stats_file = test.calculate_and_save_statistics()
    print(f"\n✅ Pruebas completadas\nArchivos generados:\n  - {csv_file}\n  - {stats_file}")

if __name__ == "__main__":
    main()

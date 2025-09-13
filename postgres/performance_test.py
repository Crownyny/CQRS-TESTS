#!/usr/bin/env python3
"""
Script de pruebas de rendimiento para aplicación CQRS
Realiza 50 inserciones y 50 consultas, midiendo tiempos y generando estadísticas
"""

import requests
import time
import csv
import statistics
import json
from datetime import datetime
import random
import string

# Configuración
BASE_URL = "http://localhost:5100"
NUM_OPERATIONS = 50

class PerformanceTest:
    def __init__(self):
        self.results = []
        self.post_ids = []
    
    def generate_random_content(self, length=50):
        """Genera contenido aleatorio para los posts"""
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    def test_post_insertion(self):
        """Prueba inserción de un post y retorna el tiempo en ms"""
        post_data = {
            "content": self.generate_random_content()
        }
        
        start_time = time.perf_counter()
        try:
            response = requests.post(f"{BASE_URL}/post", 
                                   json=post_data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            end_time = time.perf_counter()
            
            if response.status_code == 200:
                response_data = response.json()
                post_id = response_data.get('id')
                if post_id:
                    self.post_ids.append(post_id)
                
                duration_ms = (end_time - start_time) * 1000
                return duration_ms, True, response.status_code
            else:
                duration_ms = (end_time - start_time) * 1000
                return duration_ms, False, response.status_code
                
        except requests.exceptions.RequestException as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print(f"Error en inserción: {e}")
            return duration_ms, False, -1
    
    def test_post_query(self, post_id):
        """Prueba consulta de un post por ID y retorna el tiempo en ms"""
        start_time = time.perf_counter()
        try:
            response = requests.get(f"{BASE_URL}/post/{post_id}", timeout=10)
            end_time = time.perf_counter()
            
            duration_ms = (end_time - start_time) * 1000
            success = response.status_code == 200
            return duration_ms, success, response.status_code
            
        except requests.exceptions.RequestException as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print(f"Error en consulta para ID {post_id}: {e}")
            return duration_ms, False, -1
    
    def run_insertion_tests(self):
        """Ejecuta las pruebas de inserción"""
        print(f"Ejecutando {NUM_OPERATIONS} pruebas de inserción...")
        
        for i in range(NUM_OPERATIONS):
            duration_ms, success, status_code = self.test_post_insertion()
            
            result = {
                'operation_type': 'INSERT',
                'operation_number': i + 1,
                'duration_ms': duration_ms,
                'success': success,
                'status_code': status_code,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"  Inserción {i+1}: {duration_ms:.2f}ms - {'✓' if success else '✗'}")
            
            # Pequeña pausa entre operaciones
            time.sleep(0.1)
    
    def run_query_tests(self):
        """Ejecuta las pruebas de consulta"""
        print(f"\nEjecutando {NUM_OPERATIONS} pruebas de consulta...")
        
        # Si no tenemos suficientes IDs de posts creados, usamos IDs aleatorios
        available_ids = self.post_ids.copy()
        
        for i in range(NUM_OPERATIONS):
            if available_ids:
                # Usar un ID existente
                post_id = random.choice(available_ids)
            else:
                # Usar un ID aleatorio (puede no existir)
                post_id = random.randint(1, 1000)
            
            duration_ms, success, status_code = self.test_post_query(post_id)
            
            result = {
                'operation_type': 'QUERY',
                'operation_number': i + 1,
                'duration_ms': duration_ms,
                'success': success,
                'status_code': status_code,
                'post_id': post_id,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            print(f"  Consulta {i+1} (ID {post_id}): {duration_ms:.2f}ms - {'✓' if success else '✗'}")
            
            # Pequeña pausa entre operaciones
            time.sleep(0.1)
    
    def save_csv_results(self):
        """Guarda los resultados en un archivo CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_results_{timestamp}.csv"
        
        fieldnames = ['operation_type', 'operation_number', 'duration_ms', 'success', 
                     'status_code', 'post_id', 'timestamp']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                # Agregar post_id solo para queries
                if result['operation_type'] == 'INSERT':
                    result_copy = result.copy()
                    result_copy['post_id'] = ''
                else:
                    result_copy = result
                writer.writerow(result_copy)
        
        print(f"\n📁 Resultados guardados en: {filename}")
        return filename
    
    def calculate_and_save_statistics(self):
        """Calcula estadísticas y las guarda en un archivo TXT"""
        # Separar resultados por tipo de operación
        insert_times = [r['duration_ms'] for r in self.results if r['operation_type'] == 'INSERT' and r['success']]
        query_times = [r['duration_ms'] for r in self.results if r['operation_type'] == 'QUERY' and r['success']]
        all_times = insert_times + query_times
        
        # Contar operaciones exitosas
        insert_success = len(insert_times)
        query_success = len(query_times)
        insert_total = len([r for r in self.results if r['operation_type'] == 'INSERT'])
        query_total = len([r for r in self.results if r['operation_type'] == 'QUERY'])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_statistics_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ESTADÍSTICAS DE RENDIMIENTO - APLICACIÓN CQRS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"URL base: {BASE_URL}\n")
            f.write(f"Número de operaciones por tipo: {NUM_OPERATIONS}\n\n")
            
            # Estadísticas de éxito
            f.write("RESUMEN DE OPERACIONES:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Inserciones exitosas: {insert_success}/{insert_total} ({insert_success/insert_total*100:.1f}%)\n")
            f.write(f"Consultas exitosas: {query_success}/{query_total} ({query_success/query_total*100:.1f}%)\n\n")
            
            # Estadísticas de tiempo para inserciones
            if insert_times:
                f.write("ESTADÍSTICAS DE INSERCIONES (ms):\n")
                f.write("-" * 35 + "\n")
                f.write(f"Promedio: {statistics.mean(insert_times):.2f}\n")
                f.write(f"Mediana: {statistics.median(insert_times):.2f}\n")
                f.write(f"Mínimo: {min(insert_times):.2f}\n")
                f.write(f"Máximo: {max(insert_times):.2f}\n")
                if len(insert_times) > 1:
                    f.write(f"Desviación estándar: {statistics.stdev(insert_times):.2f}\n")
                f.write(f"Varianza: {statistics.variance(insert_times):.2f}\n\n")
            
            # Estadísticas de tiempo para consultas
            if query_times:
                f.write("ESTADÍSTICAS DE CONSULTAS (ms):\n")
                f.write("-" * 33 + "\n")
                f.write(f"Promedio: {statistics.mean(query_times):.2f}\n")
                f.write(f"Mediana: {statistics.median(query_times):.2f}\n")
                f.write(f"Mínimo: {min(query_times):.2f}\n")
                f.write(f"Máximo: {max(query_times):.2f}\n")
                if len(query_times) > 1:
                    f.write(f"Desviación estándar: {statistics.stdev(query_times):.2f}\n")
                f.write(f"Varianza: {statistics.variance(query_times):.2f}\n\n")
            
            # Estadísticas generales
            if all_times:
                f.write("ESTADÍSTICAS GENERALES (ms):\n")
                f.write("-" * 30 + "\n")
                f.write(f"Promedio general: {statistics.mean(all_times):.2f}\n")
                f.write(f"Mediana general: {statistics.median(all_times):.2f}\n")
                f.write(f"Mínimo general: {min(all_times):.2f}\n")
                f.write(f"Máximo general: {max(all_times):.2f}\n")
                if len(all_times) > 1:
                    f.write(f"Desviación estándar general: {statistics.stdev(all_times):.2f}\n")
                f.write(f"Varianza general: {statistics.variance(all_times):.2f}\n\n")
            
            # Comparación COMMAND vs QUERY
            if insert_times and query_times:
                f.write("COMPARACIÓN COMMAND vs QUERY:\n")
                f.write("-" * 35 + "\n")
                avg_insert = statistics.mean(insert_times)
                avg_query = statistics.mean(query_times)
                f.write(f"Promedio INSERT: {avg_insert:.2f} ms\n")
                f.write(f"Promedio QUERY: {avg_query:.2f} ms\n")
                
                if avg_insert > avg_query:
                    ratio = avg_insert / avg_query
                    f.write(f"Las inserciones son {ratio:.2f}x más lentas que las consultas\n")
                else:
                    ratio = avg_query / avg_insert
                    f.write(f"Las consultas son {ratio:.2f}x más lentas que las inserciones\n")
        
        print(f"📊 Estadísticas guardadas en: {filename}")
        return filename
    
    def print_summary(self):
        """Imprime un resumen en la consola"""
        insert_times = [r['duration_ms'] for r in self.results if r['operation_type'] == 'INSERT' and r['success']]
        query_times = [r['duration_ms'] for r in self.results if r['operation_type'] == 'QUERY' and r['success']]
        
        print("\n" + "="*60)
        print("RESUMEN DE RENDIMIENTO")
        print("="*60)
        
        if insert_times:
            print(f"INSERCIONES: {len(insert_times)} exitosas")
            print(f"  Promedio: {statistics.mean(insert_times):.2f} ms")
            if len(insert_times) > 1:
                print(f"  Desv. estándar: {statistics.stdev(insert_times):.2f} ms")
        
        if query_times:
            print(f"CONSULTAS: {len(query_times)} exitosas")
            print(f"  Promedio: {statistics.mean(query_times):.2f} ms")
            if len(query_times) > 1:
                print(f"  Desv. estándar: {statistics.stdev(query_times):.2f} ms")


def main():
    print("🚀 Iniciando pruebas de rendimiento CQRS")
    print(f"URL: {BASE_URL}")
    print(f"Operaciones por tipo: {NUM_OPERATIONS}\n")
    
    # Verificar que el servidor esté activo
    try:
        response = requests.get(f"{BASE_URL}/actuator/health", timeout=5)
        print("✓ Servidor detectado y activo")
    except:
        print("⚠️  No se puede conectar al servidor. Asegúrate de que esté ejecutándose en", BASE_URL)
        print("   Puedes iniciar el servidor con: mvn spring-boot:run")
        return
    
    test = PerformanceTest()
    
    try:
        # Ejecutar pruebas
        test.run_insertion_tests()
        test.run_query_tests()
        
        # Guardar resultados
        csv_file = test.save_csv_results()
        stats_file = test.calculate_and_save_statistics()
        
        # Mostrar resumen
        test.print_summary()
        
        print(f"\n✅ Pruebas completadas exitosamente!")
        print(f"📄 Archivos generados:")
        print(f"   - {csv_file}")
        print(f"   - {stats_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")


if __name__ == "__main__":
    main()

# Script de Pruebas de Rendimiento CQRS

Este conjunto de scripts te permite realizar pruebas de rendimiento en tu aplicación CQRS, midiendo el tiempo de respuesta de operaciones de comando (INSERT) y consulta (QUERY).

## 📋 Funcionalidades

- **50 Inserciones**: Crea posts con contenido aleatorio
- **50 Consultas**: Consulta posts por ID
- **Medición precisa**: Captura tiempos en milisegundos usando `time.perf_counter()`
- **Archivos CSV**: Datos detallados de cada operación
- **Estadísticas completas**: Promedios, desviación estándar, medianas, etc.
- **Comparación COMMAND vs QUERY**: Análisis comparativo de rendimiento

## 🚀 Cómo usar

### Opción 1: Script automático (Recomendado)
```bash
./run_performance_test.sh
```

### Opción 2: Ejecución manual
```bash
# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar pruebas
python3 performance_test.py
```

## 📊 Archivos generados

### CSV de resultados
- **Nombre**: `performance_results_YYYYMMDD_HHMMSS.csv`
- **Contenido**: Datos detallados de cada operación
- **Columnas**:
  - `operation_type`: INSERT o QUERY
  - `operation_number`: Número de operación (1-50)
  - `duration_ms`: Tiempo en milisegundos
  - `success`: Si la operación fue exitosa
  - `status_code`: Código de respuesta HTTP
  - `post_id`: ID del post (solo para queries)
  - `timestamp`: Marca de tiempo ISO

### TXT de estadísticas
- **Nombre**: `performance_statistics_YYYYMMDD_HHMMSS.txt`
- **Contenido**: Estadísticas calculadas
- **Incluye**:
  - Resumen de operaciones exitosas
  - Estadísticas de inserciones (promedio, desviación estándar, min, max)
  - Estadísticas de consultas (promedio, desviación estándar, min, max)
  - Estadísticas generales
  - Comparación COMMAND vs QUERY

## ⚙️ Configuración

Puedes modificar las siguientes variables en `performance_test.py`:

```python
BASE_URL = "http://localhost:8080"  # URL de tu aplicación
NUM_OPERATIONS = 50                 # Número de operaciones por tipo
```

## 📋 Prerrequisitos

1. **Aplicación CQRS ejecutándose**: 
   ```bash
   mvn spring-boot:run
   ```
   
2. **Python 3** instalado

3. **pip3** para instalar dependencias

## 🔍 Ejemplo de uso completo

1. **Inicia tu aplicación CQRS**:
   ```bash
   mvn spring-boot:run
   ```

2. **En otra terminal, ejecuta las pruebas**:
   ```bash
   ./run_performance_test.sh
   ```

3. **Revisa los archivos generados**:
   - `performance_results_20231212_143000.csv`
   - `performance_statistics_20231212_143000.txt`

## 📈 Ejemplo de salida

```
🚀 Iniciando pruebas de rendimiento CQRS
URL: http://localhost:8080
Operaciones por tipo: 50

✓ Servidor detectado y activo
Ejecutando 50 pruebas de inserción...
  Inserción 1: 45.23ms - ✓
  Inserción 2: 38.91ms - ✓
  ...

Ejecutando 50 pruebas de consulta...
  Consulta 1 (ID 123): 12.45ms - ✓
  Consulta 2 (ID 124): 9.87ms - ✓
  ...

============================================================
RESUMEN DE RENDIMIENTO
============================================================
INSERCIONES: 50 exitosas
  Promedio: 42.15 ms
  Desv. estándar: 8.34 ms
CONSULTAS: 50 exitosas
  Promedio: 11.23 ms
  Desv. estándar: 3.21 ms

✅ Pruebas completadas exitosamente!
📄 Archivos generados:
   - performance_results_20231212_143000.csv
   - performance_statistics_20231212_143000.txt
```

## 🛠️ Personalización

### Modificar tipos de contenido
En la función `generate_random_content()` puedes cambiar el tipo y longitud del contenido generado.

### Agregar más operaciones
Puedes extender el script para incluir:
- Pruebas de comentarios (`/post/{postId}/comment`)
- Pruebas de reacciones (`/post/{postId}/comment/{commentId}/reaction`)
- Pruebas de carga concurrente

### Cambiar formato de salida
Modifica las funciones `save_csv_results()` y `calculate_and_save_statistics()` para personalizar el formato de salida.

## 🐛 Solución de problemas

### Error de conexión
```
⚠️  No se puede conectar al servidor
```
**Solución**: Asegúrate de que tu aplicación Spring Boot esté ejecutándose en `http://localhost:8080`

### Dependencias faltantes
```
❌ ModuleNotFoundError: No module named 'requests'
```
**Solución**: Ejecuta `pip3 install -r requirements.txt`

### Permisos de ejecución
```
Permission denied
```
**Solución**: Ejecuta `chmod +x run_performance_test.sh performance_test.py`

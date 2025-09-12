#!/bin/bash

echo "🔧 Script de pruebas de rendimiento CQRS"
echo "========================================"

# Verificar si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✓ Python 3 detectado: $(python3 --version)"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

# Dar permisos de ejecución al script
chmod +x performance_test.py

echo ""
echo "🚀 Ejecutando pruebas de rendimiento..."
echo "   Esto realizará:"
echo "   - 50 inserciones de posts"
echo "   - 50 consultas de posts"
echo "   - Generará archivos CSV y TXT con resultados"
echo ""

# Ejecutar el script de pruebas
python3 performance_test.py

echo ""
echo "✅ Script de pruebas completado!"
echo "📁 Revisa los archivos generados en el directorio actual"

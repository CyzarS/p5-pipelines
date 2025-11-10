#!/bin/bash

# Script para probar la API localmente

BASE_URL="http://localhost:5000"

echo "======================================"
echo "Probando API de Productos"
echo "======================================"
echo ""

# Test 1: Health Check
echo "1. Health Check"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

# Test 2: Obtener información de la API
echo "2. Información de la API"
curl -s "$BASE_URL/" | python3 -m json.tool
echo -e "\n"

# Test 3: Crear un producto
echo "3. Crear un producto"
PRODUCTO_ID=$(curl -s -X POST "$BASE_URL/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell",
    "precio": 15999.99,
    "descripcion": "Laptop Dell Inspiron 15",
    "stock": 10
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['producto']['id'])")

echo "Producto creado con ID: $PRODUCTO_ID"
echo -e "\n"

# Test 4: Obtener todos los productos
echo "4. Obtener todos los productos"
curl -s "$BASE_URL/productos" | python3 -m json.tool
echo -e "\n"

# Test 5: Obtener un producto específico
echo "5. Obtener producto específico"
curl -s "$BASE_URL/productos/$PRODUCTO_ID" | python3 -m json.tool
echo -e "\n"

# Test 6: Actualizar el producto
echo "6. Actualizar producto"
curl -s -X PUT "$BASE_URL/productos/$PRODUCTO_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell Actualizada",
    "precio": 14999.99,
    "stock": 15
  }' | python3 -m json.tool
echo -e "\n"

# Test 7: Eliminar el producto
echo "7. Eliminar producto"
curl -s -X DELETE "$BASE_URL/productos/$PRODUCTO_ID" | python3 -m json.tool
echo -e "\n"

echo "======================================"
echo "Pruebas completadas"
echo "======================================"

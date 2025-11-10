import os
import boto3
from flask import Flask, request, jsonify
from decimal import Decimal
from datetime import datetime
import uuid

app = Flask(__name__)

# Configuración desde variables de entorno
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
TABLE_NAME = f"productos_{ENVIRONMENT}"

# Configurar cliente DynamoDB
dynamodb_config = {
    'region_name': AWS_REGION
}

# Para ambiente local, permitir endpoint personalizado
if ENVIRONMENT == 'local' and os.getenv('DYNAMODB_ENDPOINT'):
    dynamodb_config['endpoint_url'] = os.getenv('DYNAMODB_ENDPOINT')

dynamodb = boto3.resource('dynamodb', **dynamodb_config)
table = dynamodb.Table(TABLE_NAME)

def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@app.route('/')
def home():
    return jsonify({
        'message': 'API de Productos',
        'environment': ENVIRONMENT,
        'table': TABLE_NAME,
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Endpoint de health check"""
    try:
        # Verificar conexión a DynamoDB
        table.table_status
        return jsonify({
            'status': 'healthy',
            'environment': ENVIRONMENT,
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'environment': ENVIRONMENT,
            'error': str(e)
        }), 503

# CREATE - Crear un producto
@app.route('/productos', methods=['POST'])
def create_producto():
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data or 'nombre' not in data or 'precio' not in data:
            return jsonify({'error': 'nombre y precio son campos requeridos'}), 400
        
        producto_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'id': producto_id,
            'nombre': data['nombre'],
            'precio': Decimal(str(data['precio'])),
            'descripcion': data.get('descripcion', ''),
            'stock': data.get('stock', 0),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        table.put_item(Item=item)
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto': item
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READ - Obtener todos los productos
@app.route('/productos', methods=['GET'])
def get_productos():
    try:
        response = table.scan()
        productos = response.get('Items', [])
        
        return jsonify({
            'count': len(productos),
            'productos': productos
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READ - Obtener un producto por ID
@app.route('/productos/<string:producto_id>', methods=['GET'])
def get_producto(producto_id):
    try:
        response = table.get_item(Key={'id': producto_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify(response['Item']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# UPDATE - Actualizar un producto
@app.route('/productos/<string:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        # Verificar que el producto existe
        response = table.get_item(Key={'id': producto_id})
        if 'Item' not in response:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Construir expresión de actualización
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        
        if 'nombre' in data:
            update_expression += ", nombre = :nombre"
            expression_values[':nombre'] = data['nombre']
        
        if 'precio' in data:
            update_expression += ", precio = :precio"
            expression_values[':precio'] = Decimal(str(data['precio']))
        
        if 'descripcion' in data:
            update_expression += ", descripcion = :descripcion"
            expression_values[':descripcion'] = data['descripcion']
        
        if 'stock' in data:
            update_expression += ", stock = :stock"
            expression_values[':stock'] = data['stock']
        
        response = table.update_item(
            Key={'id': producto_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'producto': response['Attributes']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE - Eliminar un producto
@app.route('/productos/<string:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    try:
        # Verificar que el producto existe
        response = table.get_item(Key={'id': producto_id})
        if 'Item' not in response:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        table.delete_item(Key={'id': producto_id})
        
        return jsonify({
            'message': 'Producto eliminado exitosamente',
            'id': producto_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = ENVIRONMENT == 'local'
    
    print(f"Iniciando aplicación en ambiente: {ENVIRONMENT}")
    print(f"Tabla DynamoDB: {TABLE_NAME}")
    print(f"Puerto: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

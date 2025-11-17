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
TABLE_NAME = os.getenv('TABLE_NAME', f"productos_{ENVIRONMENT}")

# Configurar cliente DynamoDB
dynamodb_config = {
    'region_name': AWS_REGION
}

# Tanto local como prod usan AWS en la nube (productos_local y productos_prod respectivamente)
# Soportar AWS Academy (con session token) y cuentas regulares
if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
    dynamodb_config['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
    dynamodb_config['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    # AWS Academy requiere session token
    if os.getenv('AWS_SESSION_TOKEN'):
        dynamodb_config['aws_session_token'] = os.getenv('AWS_SESSION_TOKEN')

dynamodb = boto3.resource('dynamodb', **dynamodb_config)
table = dynamodb.Table(TABLE_NAME)

def decimal_default(obj):
    """Helper para serializar Decimal a JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def convert_decimals(obj):
    """Convierte Decimals a float recursivamente"""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

@app.route('/')
def home():
    return jsonify({
        'message': 'API de Productos - Práctica 5 CI/CD',
        'environment': ENVIRONMENT,
        'table': TABLE_NAME,
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'create': 'POST /productos',
            'list': 'GET /productos',
            'get': 'GET /productos/<id>',
            'update': 'PUT /productos/<id>',
            'delete': 'DELETE /productos/<id>'
        }
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
            'table': TABLE_NAME,
            'database': 'connected',
            'region': AWS_REGION
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
    """
    Crear un nuevo producto
    Body: {
        "nombre": "string (requerido)",
        "precio": "number (requerido)",
        "descripcion": "string (opcional)",
        "stock": "integer (opcional, default: 0)"
    }
    """
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data or 'nombre' not in data or 'precio' not in data:
            return jsonify({'error': 'nombre y precio son campos requeridos'}), 400
        
        # Validar que precio sea numérico
        try:
            precio = float(data['precio'])
            if precio < 0:
                return jsonify({'error': 'El precio no puede ser negativo'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'El precio debe ser un número válido'}), 400
        
        producto_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'id': producto_id,
            'nombre': data['nombre'].strip(),
            'precio': Decimal(str(precio)),
            'descripcion': data.get('descripcion', '').strip(),
            'stock': int(data.get('stock', 0)),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        table.put_item(Item=item)
        
        # Convertir Decimals para la respuesta JSON
        response_item = convert_decimals(item)
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto': response_item
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READ - Obtener todos los productos
@app.route('/productos', methods=['GET'])
def get_productos():
    """
    Listar todos los productos
    """
    try:
        response = table.scan()
        productos = response.get('Items', [])
        
        # Convertir Decimals para la respuesta JSON
        productos = convert_decimals(productos)
        
        return jsonify({
            'count': len(productos),
            'productos': productos
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READ - Obtener un producto por ID
@app.route('/productos/<string:producto_id>', methods=['GET'])
def get_producto(producto_id):
    """
    Obtener un producto específico por ID
    """
    try:
        response = table.get_item(Key={'id': producto_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Convertir Decimals para la respuesta JSON
        producto = convert_decimals(response['Item'])
        
        return jsonify(producto), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# UPDATE - Actualizar un producto
@app.route('/productos/<string:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    """
    Actualizar un producto existente
    Body: {
        "nombre": "string (opcional)",
        "precio": "number (opcional)",
        "descripcion": "string (opcional)",
        "stock": "integer (opcional)"
    }
    """
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
            expression_values[':nombre'] = data['nombre'].strip()
        
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio < 0:
                    return jsonify({'error': 'El precio no puede ser negativo'}), 400
                update_expression += ", precio = :precio"
                expression_values[':precio'] = Decimal(str(precio))
            except (ValueError, TypeError):
                return jsonify({'error': 'El precio debe ser un número válido'}), 400
        
        if 'descripcion' in data:
            update_expression += ", descripcion = :descripcion"
            expression_values[':descripcion'] = data['descripcion'].strip()
        
        if 'stock' in data:
            update_expression += ", stock = :stock"
            expression_values[':stock'] = int(data['stock'])
        
        response = table.update_item(
            Key={'id': producto_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        # Convertir Decimals para la respuesta JSON
        producto = convert_decimals(response['Attributes'])
        
        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'producto': producto
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE - Eliminar un producto
@app.route('/productos/<string:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    """
    Eliminar un producto por ID
    """
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
    port = int(os.getenv('PORT', 5002))
    debug = ENVIRONMENT == 'local'
    

    print("Práctica 5 CI/CD ")

    print(f" Ambiente: {ENVIRONMENT}")
    print(f" Tabla DynamoDB: {TABLE_NAME}")
    print(f"Región AWS: {AWS_REGION}")
    print(f" Puerto: {port}")
    print(f"Debug: {debug}")
    print("══════════════════════════════════════════════════════════════")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

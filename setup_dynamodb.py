#!/usr/bin/env python3
"""
Script para crear las tablas de DynamoDB para la aplicación de productos
"""

import boto3
import os
import sys

def crear_tabla(dynamodb, table_name):
    """Crea una tabla de DynamoDB para productos"""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f" Creando tabla {table_name}...")
        table.wait_until_exists()
        print(f" Tabla {table_name} creada exitosamente")
        
        return True
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"  La tabla {table_name} ya existe")
        return True
    except Exception as e:
        print(f" Error al crear tabla {table_name}: {str(e)}")
        return False

def main():
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"🔧 Configurando DynamoDB en AWS")
    print(f"☁️  Conectando a DynamoDB en AWS ({aws_region})")
    
    config = {'region_name': aws_region}
    
    # Soportar AWS Academy (con session token) y cuentas regulares
    if os.getenv('AWS_SESSION_TOKEN'):
        print("🎓 Usando credenciales de AWS Academy")
        config['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
        config['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
        config['aws_session_token'] = os.getenv('AWS_SESSION_TOKEN')
    elif os.getenv('AWS_ACCESS_KEY_ID'):
        print("Usando credenciales explícitas")
        config['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
        config['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    else:
        print("Usando credenciales del entorno (IAM role)")
    
    dynamodb = boto3.resource('dynamodb', **config)
    
    # Crear tablas para ambos ambientes
    tablas = ['productos_local', 'productos_prod']
    
    exito = True
    for tabla in tablas:
        if not crear_tabla(dynamodb, tabla):
            exito = False
    
    if exito:
        print("\n Todas las tablas fueron creadas/verificadas correctamente")
        
        print("\n Tablas disponibles:")
        tables = list(dynamodb.tables.all())
        for table in tables:
            print(f"  - {table.name}")
        
        return 0
    else:
        print("\n Hubo errores al crear algunas tablas")
        return 1

if __name__ == '__main__':
    sys.exit(main())

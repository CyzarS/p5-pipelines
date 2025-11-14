#!/usr/bin/env python3
"""
Script para crear las tablas de DynamoDB necesarias para la aplicación
"""
import boto3
import sys
import os

def create_table(dynamodb, table_name):
    """Crear tabla en DynamoDB"""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
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
        
        print(f"Creando tabla {table_name}...")
        table.wait_until_exists()
        print(f" Tabla {table_name} creada exitosamente")
        return True
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f" La tabla {table_name} ya existe")
        return True
    except Exception as e:
        print(f" Error al crear tabla {table_name}: {str(e)}")
        return False

def main():
    """Función principal"""
    # Configurar región
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"Región AWS: {region}")
    print("="*50)
    
    # Crear cliente DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=region)
    
    # Crear tablas para ambos ambientes
    tables = ['productos_local', 'productos_prod']
    
    success = True
    for table_name in tables:
        if not create_table(dynamodb, table_name):
            success = False
    
    print("="*50)
    if success:
        print(" Todas las tablas fueron creadas exitosamente")
        return 0
    else:
        print(" Hubo errores al crear algunas tablas")
        return 1

if __name__ == '__main__':
    sys.exit(main())

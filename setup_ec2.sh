#!/bin/bash

# Script para configurar una instancia EC2 con Docker
# Ejecutar este script en tu instancia EC2 de AWS Academy

echo "======================================"
echo "Configurando instancia EC2"
echo "======================================"

# Actualizar sistema
echo "Actualizando sistema..."
sudo yum update -y

# Instalar Docker
echo "Instalando Docker..."
sudo yum install docker -y

# Iniciar servicio Docker
echo "Iniciando Docker..."
sudo service docker start

# Habilitar Docker al inicio
sudo systemctl enable docker

# Agregar usuario ec2-user al grupo docker
echo "Configurando permisos de Docker..."
sudo usermod -a -G docker ec2-user

# Instalar docker-compose (opcional pero útil)
echo "Instalando docker-compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
echo ""
echo "======================================"
echo "Verificando instalación..."
echo "======================================"
docker --version
docker-compose --version

echo ""
echo "======================================"
echo "✓ Configuración completada"
echo "======================================"
echo ""
echo "IMPORTANTE: Cierra sesión y vuelve a conectarte para que"
echo "los cambios de grupo tomen efecto (comando: exit)"
echo ""
echo "Después de reconectar, verifica con: docker ps"

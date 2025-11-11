# Práctica 5 - CI/CD Pipeline con AWS Academy

API REST de productos con implementación completa de CI/CD usando GitHub Actions, Docker y AWS.

## Descripción del Proyecto

Aplicación CRUD de productos que implementa:
- **12 Factores**: Configuración por variables de entorno, separación de ambientes
- **CI/CD**: Pipeline automatizado con GitHub Actions
- **Contenedores**: Docker para portabilidad
- **Cloud**: DynamoDB para persistencia, EC2 para despliegue

## Arquitectura

```
GitHub → GitHub Actions → Docker Hub → EC2
                ↓
            DynamoDB (productos_local / productos_prod)
```

## Requisitos Previos

### En tu máquina local:
- Python 3.9+
- Git
- Cuenta de Docker Hub
- Cuenta de GitHub

### En AWS Academy:
- Acceso a AWS Academy Learner Lab
- Permisos para crear: EC2, DynamoDB, Security Groups

## Configuración Paso a Paso

### 1. Configuración de AWS Academy

#### 1.1. Crear tablas en DynamoDB

```bash
# Configurar credenciales de AWS Academy
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_SESSION_TOKEN="tu_session_token"
export AWS_REGION="us-east-1"

# Ejecutar script de setup
python3 setup_dynamodb.py
```

#### 1.2. Crear y configurar instancia EC2

**Crear instancia:**
1. Ir a EC2 → Launch Instance
2. Nombre: `practica-5-cicd`
3. AMI: Amazon Linux 2023
4. Tipo: t2.micro (o t3.micro)
5. Key pair: Crear o usar existente (guardar archivo .pem)
6. Security Group: Crear con reglas:
   - SSH (22) desde Mi IP
   - HTTP (80) desde 0.0.0.0/0
   - HTTPS (443) desde 0.0.0.0/0

**Configurar Docker en EC2:**

```bash
# Conectarse a EC2
ssh -i "tu-keypair.pem" ec2-user@tu-ip-publica

# Copiar y ejecutar setup_ec2.sh
# O ejecutar comandos manualmente:
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Cerrar sesión y reconectar
exit
ssh -i "tu-keypair.pem" ec2-user@tu-ip-publica

# Verificar
docker ps
```

### 2. Configuración de Docker Hub

1. Crear cuenta en https://hub.docker.com
2. Crear repositorio público: `productos-api`
3. Generar Access Token:
   - Settings → Security → New Access Token
   - Nombre: `github-actions`
   - Guardar el token

### 3. Configuración de GitHub

#### 3.1. Crear repositorio

```bash
# En tu máquina local
git init
git add .
git commit -m "Initial commit: Práctica 5 CI/CD"
git branch -M main
git remote add origin https://github.com/tu-usuario/practica-5-cicd.git
git push -u origin main
```

#### 3.2. Configurar Secrets

Ir a: Settings → Secrets and variables → Actions → New repository secret

Agregar los siguientes secrets:

**Docker Hub:**
- `DOCKERHUB_USERNAME`: tu usuario de Docker Hub
- `DOCKERHUB_TOKEN`: el token generado

**AWS (actualizar cada sesión de AWS Academy):**
- `AWS_ACCESS_KEY_ID`: de AWS Academy
- `AWS_SECRET_ACCESS_KEY`: de AWS Academy
- `AWS_SESSION_TOKEN`: de AWS Academy

**EC2:**
- `EC2_HOST`: IP pública de tu instancia
- `EC2_USER`: `ec2-user` (default para Amazon Linux)
- `EC2_SSH_KEY`: contenido completo del archivo .pem

> **IMPORTANTE**: Los secrets de AWS expiran cuando termina tu sesión de AWS Academy. Debes actualizarlos cada vez que inicies el laboratorio.

### 4. Pruebas Locales

#### 4.1. Configurar ambiente local

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

#### 4.2. Ejecutar localmente

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
export ENVIRONMENT=local
python app.py
```

#### 4.3. Probar endpoints

```bash
# Ejecutar script de pruebas
./test_api.sh

# O manualmente:
curl http://localhost:5000/health
curl http://localhost:5000/productos
```

### 5. Despliegue Automático

Una vez configurado todo:

```bash
# Hacer cambios en el código
git add .
git commit -m "Descripción del cambio"
git push origin main

# El pipeline se ejecutará automáticamente
```

Monitorear el pipeline en: GitHub → Actions

## Estructura del Proyecto

```
practica-5-cicd/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # Pipeline de CI/CD
├── app.py                      # Aplicación Flask
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Imagen Docker
├── .env.example                # Ejemplo de variables
├── .gitignore                  # Archivos ignorados
├── setup_dynamodb.py           # Script para crear tablas
├── setup_ec2.sh                # Script para configurar EC2
├── test_api.sh                 # Script para probar API
└── README.md                   # Esta documentación
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Productos

**Listar todos:**
```bash
GET /productos
```

**Obtener uno:**
```bash
GET /productos/{id}
```

**Crear:**
```bash
POST /productos
Content-Type: application/json

{
  "nombre": "Producto",
  "precio": 100.00,
  "descripcion": "Descripción",
  "stock": 10
}
```

**Actualizar:**
```bash
PUT /productos/{id}
Content-Type: application/json

{
  "nombre": "Producto Actualizado",
  "precio": 150.00,
  "stock": 20
}
```

**Eliminar:**
```bash
DELETE /productos/{id}
```

## Pipeline CI/CD

El pipeline consta de 3 etapas:

### 1. Build 
- Checkout del código
- Instalación de dependencias
- Validación de sintaxis (flake8)
- Verificación de archivos requeridos

### 2. Docker 
- Build de imagen Docker
- Versionado automático (SHA, fecha)
- Push a Docker Hub
- Cache para optimizar builds

### 3. Deploy
- Conexión SSH a EC2
- Pull de imagen desde Docker Hub
- Despliegue del contenedor
- Health check post-deploy

## Factores de 12-Factor App Implementados

1. **Codebase**: Un repositorio, múltiples deploys
2. **Dependencies**: requirements.txt explícito
3. **Config**: Variables de entorno (.env, secrets)
4. **Backing Services**: DynamoDB como servicio externo
5. **Build, Release, Run**: Etapas separadas en CI/CD
6. **Processes**: Aplicación stateless
7. **Port Binding**: Flask en puerto configurable
8. **Concurrency**: Gunicorn con workers
9. **Disposability**: Contenedores efímeros
10. **Dev/Prod Parity**: Misma imagen, diferente config
11. **Logs**: Stdout/stderr (Docker logs)
12. **Admin Processes**: Scripts de migración disponibles

## Solución de Problemas

### Error: Credenciales AWS expiradas
```bash
# Actualizar secrets en GitHub con nuevas credenciales de AWS Academy
```

### Error: Puerto 80 ocupado en EC2
```bash
# Ver qué está usando el puerto
sudo netstat -tlnp | grep :80

# Detener contenedor anterior
docker stop productos-api
docker rm productos-api
```

### Error: No se puede conectar a DynamoDB
```bash
# Verificar que las tablas existen
aws dynamodb list-tables --region us-east-1

# Verificar permisos de IAM
aws sts get-caller-identity
```

### Error: SSH a EC2 falla
```bash
# Verificar formato de clave (debe terminar con newline)
# Verificar permisos de Security Group
# Verificar que la IP pública es correcta
```


## Testing

### Pruebas manuales en producción

```bash
# Reemplazar con tu IP de EC2
export EC2_IP="tu-ip-publica"

# Health check
curl http://$EC2_IP/health

# Crear producto
curl -X POST http://$EC2_IP/productos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","precio":100,"stock":5}'

# Listar productos
curl http://$EC2_IP/productos
```

## Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de Docker](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [AWS DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [12-Factor App](https://12factor.net/)

## Autor

César - Arquitectura de Software

## Licencia

Este proyecto es para fines educativos.

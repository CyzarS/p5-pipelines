.PHONY: help install run test docker-build docker-run docker-stop clean setup-aws update-secrets

help:
	@echo "Comandos disponibles:"
	@echo "  make install        - Instalar dependencias Python"
	@echo "  make run           - Ejecutar aplicación localmente"
	@echo "  make test          - Ejecutar pruebas de la API"
	@echo "  make docker-build  - Construir imagen Docker"
	@echo "  make docker-run    - Ejecutar contenedor Docker"
	@echo "  make docker-stop   - Detener contenedor Docker"
	@echo "  make setup-aws     - Configurar tablas DynamoDB"
	@echo "  make update-secrets - Actualizar secrets de GitHub"
	@echo "  make clean         - Limpiar archivos temporales"

install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt
	@echo "✓ Dependencias instaladas"

run:
	@echo "Ejecutando aplicación en modo local..."
	@export ENVIRONMENT=local && python app.py

test:
	@echo "Probando API..."
	@chmod +x test_api.sh
	@./test_api.sh

docker-build:
	@echo "Construyendo imagen Docker..."
	docker build -t productos-api:local .
	@echo "✓ Imagen construida: productos-api:local"

docker-run:
	@echo "Ejecutando contenedor Docker..."
	docker run -d \
		--name productos-api-local \
		-p 5000:5000 \
		-e ENVIRONMENT=local \
		-e AWS_REGION=${AWS_REGION} \
		-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		-e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
		productos-api:local
	@echo "✓ Contenedor corriendo en http://localhost:5000"
	@echo "  Ver logs: docker logs -f productos-api-local"

docker-stop:
	@echo "Deteniendo contenedor..."
	@docker stop productos-api-local 2>/dev/null || true
	@docker rm productos-api-local 2>/dev/null || true
	@echo "✓ Contenedor detenido"

docker-compose-up:
	@echo "Iniciando con docker-compose..."
	docker-compose up -d
	@echo "✓ Aplicación corriendo en http://localhost:5000"

docker-compose-down:
	@echo "Deteniendo docker-compose..."
	docker-compose down
	@echo "✓ Servicios detenidos"

setup-aws:
	@echo "Configurando tablas DynamoDB..."
	@chmod +x setup_dynamodb.py
	python3 setup_dynamodb.py
	@echo "✓ Tablas configuradas"

update-secrets:
	@echo "Actualizando secrets de GitHub..."
	@chmod +x update_secrets.sh
	@./update_secrets.sh

clean:
	@echo "Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Limpieza completada"

lint:
	@echo "Ejecutando linter..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "✓ Linting completado"

logs:
	@echo "Mostrando logs del contenedor..."
	docker logs -f productos-api-local

status:
	@echo "Estado de la aplicación:"
	@echo ""
	@echo "Contenedores Docker:"
	@docker ps -a | grep productos-api || echo "  Ningún contenedor corriendo"
	@echo ""
	@echo "Imágenes Docker:"
	@docker images | grep productos-api || echo "  Ninguna imagen local"
	@echo ""

all: clean install docker-build docker-run
	@echo "✓ Aplicación lista y corriendo"

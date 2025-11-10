# Usar imagen base oficial de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5000

# Variables de entorno por defecto (se pueden sobrescribir)
ENV ENVIRONMENT=prod
ENV PORT=5000
ENV AWS_REGION=us-east-1

# Comando para ejecutar la aplicación usando gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]

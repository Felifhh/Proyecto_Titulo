# Imagen base oficial de Python
FROM python:3.13-slim

# Evitar buffering de logs
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt /app/

# Instalar dependencias Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el proyecto entero
COPY . /app/

# Exponer el puerto de Django
EXPOSE 8000

# Comando por defecto (runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

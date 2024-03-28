# Usamos una imagen de Python como base
FROM python:3.10.10

WORKDIR /app
## Instalo dependencias del backend
# Copiamos los archivos de requisitos
COPY ./requirements.txt .
# Instalamos requerimientos principales
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# Copiamos los archivos de la aplicación
# No copio porque queda montado como volumen en el compose
# COPY ./app .

# Exponemos el puerto 5000
EXPOSE 5000

FROM python:3.10.10

WORKDIR /app

# Copiamos los archivos de requisitos
COPY ./requirements.txt .

# Instalamos requerimientos principales
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copiamos el script prestart.sh
COPY ./prestart.sh .

# Damos permisos de ejecución al script prestart.sh
RUN chmod +x /app/prestart.sh

# Exponemos el puerto 5000
EXPOSE 5000

# Ejecutamos el script prestart.sh antes de iniciar la aplicación
CMD ["sh", "-c", "/app/prestart.sh"]
FROM python:3.10.10

WORKDIR /app

# Install wkhtmltopdf
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       wkhtmltopdf \
       fontconfig \
       libfontconfig1 \
       libxrender1 \
       libxext6 \
       xfonts-75dpi \
       xfonts-base \
    && rm -rf /var/lib/apt/lists/*

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
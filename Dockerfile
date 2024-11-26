# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde se ejecutará la aplicación
EXPOSE 8080

# Configurar la entrada para ejecutar la aplicación
CMD ["python", "main.py"]

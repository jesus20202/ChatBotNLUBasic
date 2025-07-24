# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia requirements.txt primero para cache
COPY requirements.txt .

# Instala herramientas de compilación, dependencias y luego limpia
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip cache purge

# Copia el resto del código
COPY . .

# Limpia archivos innecesarios
RUN find . -name "*.pyc" -delete \
    && find . -name "__pycache__" -type d -exec rm -rf {} + \
    && find . -name "*.pyo" -delete

# Expone el puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
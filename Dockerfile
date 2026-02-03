# Gunakan image Python sebagai base image
FROM python:3.9-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt dan install dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file yang ada di project ke dalam container
COPY . /app/

# Tentukan perintah untuk menjalankan bot
CMD ["python", "main.py"]
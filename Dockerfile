# Usa una imagen oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /bot

# Copia el archivo de dependencias e instálalas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu bot
COPY . .

# Comando para ejecutar tu bot (ajusta "bot.py" si tu archivo principal tiene otro nombre)
CMD ["python", "bot.py"]

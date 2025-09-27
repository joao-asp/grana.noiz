FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ ./src/

# Criar diretórios para dados
RUN mkdir -p /app/data /app/logs /app/backup

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/caixinha.db
ENV ENV=production

# Expor porta para futuras funcionalidades
EXPOSE 8000

# Executar bot
CMD ["python", "-m", "src.bot"]
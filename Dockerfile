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

# Copiar código fonte, scripts operacionais e interface web
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY web/ ./web/

# Criar diretórios para dados
RUN mkdir -p /app/data /app/logs /app/backup

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/caixinha.db
ENV WEB_HOST=0.0.0.0
ENV WEB_PORT=8080
ENV ENV=production

# Interface web
EXPOSE 8080

# Executar bot
CMD ["python", "-m", "src.bot"]
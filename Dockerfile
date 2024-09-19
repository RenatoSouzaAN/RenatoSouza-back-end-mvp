# Define a imagem base
FROM python:3.12

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte para o diretório de trabalho
COPY . .

# Configura as variáveis de ambiente para o Flask
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Remove existing database files and migrations if they exist
RUN rm -rf migrations instance dmarket.db

# Inicializa o banco de dados e aplica as migrações
RUN flask db init && \
    flask db migrate && \
    flask db upgrade

# Define o comando de execução da API
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
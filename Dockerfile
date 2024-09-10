# Utiliza uma imagem oficial do Python como base
FROM python:3.12.6-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Copia o arquivo requirements.txt para o contêiner
COPY requirements.txt ./

# Instala as dependências listadas no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o contêiner
COPY . .

# Expor a porta 8050 para que o Dash possa ser acessado
EXPOSE 8050

# Define a variável de ambiente para desativar o modo de debug no Dash
ENV DASH_DEBUG_MODE False

# Comando para iniciar a aplicação
CMD ["python", "app.py"]

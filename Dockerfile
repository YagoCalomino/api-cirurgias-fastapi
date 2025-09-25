# Etapa 1: Usa uma imagem oficial do Python como base
FROM python:3.11.9-slim-bullseye

# Etapa 2: Defini o diretório de trabalho dentro do contêiner
WORKDIR /code

# Etapa 3: Copia o arquivo de dependências para dentro do contêiner
COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install -y build-essential

# Etapa 4: Instala as dependências
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Etapa 5: Copia todo o código da nossa pasta 'app' para o contêiner
COPY ./app /code/app

# Etapa 6: Expor a porta que a aplicação vai usar
EXPOSE 10000

# Etapa 7: O comando para iniciar a aplicação quando o contêiner rodar
# -w 4: Inicia 4 "workers" (processos) para lidar com as requisições
# -k uvicorn.workers.UvicornWorker: Diz ao Gunicorn para usar o Uvicorn como o worker
# -b 0.0.0.0:10000: Faz a aplicação escutar em todas as interfaces de rede na porta 10000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:10000"]

# Adicionando essa desgraça desta linha no final do seu Dockerfile
# Forçando novo deploy em 24/09/2025
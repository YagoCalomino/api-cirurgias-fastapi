# Etapa 1: Usar uma imagem oficial do Python como base
# Esta imagem já vem com Python e ferramentas essenciais instaladas
FROM python:3.11-slim

# Etapa 2: Definir o diretório de trabalho dentro do contêiner
# Todos os comandos a seguir serão executados a partir desta pasta
WORKDIR /code

# Etapa 3: Copiar o arquivo de dependências para dentro do contêiner
COPY ./requirements.txt /code/requirements.txt

# Etapa 4: Instalar as dependências
# O '--no-cache-dir' economiza espaço na imagem final
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Etapa 5: Copiar todo o código da nossa pasta 'app' para o contêiner
COPY ./app /code/app

# Etapa 6: Expor a porta que a aplicação vai usar
# O Render espera que a porta seja a 10000
EXPOSE 10000

# Etapa 7: O comando para iniciar a aplicação quando o contêiner rodar
# Usamos o Gunicorn para iniciar o Uvicorn, o padrão para produção com FastAPI
# -w 4: Inicia 4 "workers" (processos) para lidar com as requisições
# -k uvicorn.workers.UvicornWorker: Diz ao Gunicorn para usar o Uvicorn como o worker
# -b 0.0.0.0:10000: Faz a aplicação escutar em todas as interfaces de rede na porta 10000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:10000"]

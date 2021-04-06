FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY req.txt /app

ENV NAME integral

ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8

EXPOSE 8000

RUN pip install ssh-import-id && \
 pip install ufw-config && \
 pip install psycopg2-binary && \
 pip3 install -r req.txt && \
 pip install databases
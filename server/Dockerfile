ARG OS_VERSION=22.04
FROM ubuntu:${OS_VERSION}

RUN apt update && apt -y install python3 \
    && apt -y install pip \
    && pip install psycopg2-binary

ADD source /server/
WORKDIR /server/

CMD ["python3", "main.py"]

FROM python:3.11-slim-buster
WORKDIR /app

RUN apt-get update

ARG USERNAME=tourose
ARG GROUPNAME=reptile
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID $USERNAME
USER $USERNAME

COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "main.py"]
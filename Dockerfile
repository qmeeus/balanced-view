FROM python:3.6-slim-stretch

RUN apt-get update \
    && apt-get install -y python3-pip python3-dev git \
    && pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r /requirements.txt

ENV USER=patrick
ENV UID=27328
WORKDIR "/$USER"

RUN useradd \
  --home-dir "$(pwd)" \
  --no-create-home \
  --uid "$UID" \
  "$USER" \ 
 && chown $USER:$USER .

USER $USER

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV FLASK_ENV=production

COPY --chown=$USER:$USER ./api ./api
COPY --chown=$USER:$USER ./ui ./ui
COPY --chown=$USER:$USER entrypoint.sh .
COPY --chown=$USER:$USER ./data /var/lib/sqlite

CMD [ "./entrypoint.sh" ]

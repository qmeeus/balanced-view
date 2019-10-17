FROM python:3.6-slim-stretch

RUN apt-get update \
    && apt-get install -y cron python3-pip python3-dev git \
    && python -m pip install --upgrade --no-cache-dir pip

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY install_nlp_models.sh ./
RUN chmod +x install_nlp_models.sh
RUN bash install_nlp_models.sh

ENV USER=api
ENV UID=1000
# ARG UID
WORKDIR "/$USER"

# RUN useradd \
#   --home-dir "$(pwd)" \
#   --no-create-home \
#   --uid "$UID" \
#   "$USER" \ 
#  && chown $USER:$USER .

# USER $USER

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY ./api ./api
COPY ./tests ./tests
COPY docker-entrypoint.sh .
RUN chmod 744 docker-entrypoint.sh

# CMD [ "gunicorn", "-w3", "-k", "gevent", "--bind=0.0.0.0:5000", "api.wsgi" ]
CMD [ "./docker-entrypoint.sh" ]

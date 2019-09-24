FROM python:3.6-slim-stretch

RUN apt-get update \
    && apt-get install -y cron python3-pip python3-dev git \
    && pip install --upgrade --no-cache-dir pip

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ENV USER=api
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

COPY . .

COPY data_provider/cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

RUN chmod 744 docker-entrypoint.sh

# CMD [ "gunicorn", "--chdir", "..", "-w3", "-k", "gevent", "--bind=0.0.0.0:5000", "api.wsgi" ]
CMD [ "./docker-entrypoint.sh" ]
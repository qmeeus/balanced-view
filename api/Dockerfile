FROM python:3.6-slim-stretch

RUN apt-get update \
    && apt-get install -y cron python3-pip python3-dev git \
    && pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r /requirements.txt

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

COPY . .

RUN echo 0 6 '*' '*' '*' python -m /$USER/data_provider | crontab -

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD [ "gunicorn", "--chdir", "..", "-w3", "-k", "gevent", "--bind=0.0.0.0:5000", "api.wsgi" ]

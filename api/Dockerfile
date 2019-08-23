FROM python:3.6-slim-stretch

RUN apt-get update \
    && apt-get install -y python3-pip python3-dev git \
    && pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r /requirements.txt

ENV USER=api
<<<<<<< HEAD
# ARG UID
WORKDIR "/$USER"

# RUN useradd \
#   --home-dir "$(pwd)" \
#   --no-create-home \
#   --uid "$UID" \
#   "$USER" \ 
#  && chown $USER:$USER .
=======
ARG UID
WORKDIR "/$USER"

RUN useradd \
  --home-dir "$(pwd)" \
  --no-create-home \
  --uid "$UID" \
  --gid "$UID" \
  "$USER" \ 
 && chown $USER:$USER .
>>>>>>> c14f1e9834e2b162e33f8ef63da4c43c88dd0ca6

# USER $USER

COPY . .

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD [ "gunicorn", "--chdir", "..", "-w3", "--bind=0.0.0.0:5000", "api.wsgi" ]

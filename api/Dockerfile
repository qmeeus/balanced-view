FROM python:3.7-alpine

RUN apk update && apk upgrade \
  && apk add --no-cache git gcc g++ \
  && rm -rf /var/cache/apk/*

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . .

ENV USER=patrick
ENV UID=27328
WORKDIR "/$USER"

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "$(pwd)" \
    --no-create-home \
    --uid "$UID" \
    "$USER" \
 && chown $USER:$USER .

USER $USER

CMD [ "python", "api.py" ]


# FROM python:3.6-slim-stretch

# COPY requirements.txt requirements.txt
# RUN apt-get update \
#     && apt-get install -y python3-pip python3-dev git \
#     && pip3 install --upgrade pip \
#     && pip3 install -r requirements.txt

# # Did not find a way to use build_arg with heroku
# RUN useradd --uid 1001 --shell /bin/bash --create-home patrick
# USER patrick

# WORKDIR /home/patrick
# RUN mkdir /home/patrick/src
# WORKDIR /home/patrick/src

# ENV PATH="/home/patrick/.local/bin/:$PATH"
# COPY --chown=patrick:users . /home/patrick/src/

# ENV LANG=C.UTF-8

# CMD [ "python", "api.py" ]

FROM python:3.6-stretch

COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get install -y python3-pip python3-dev \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

# Did not find a way to use build_arg with heroku
RUN useradd --uid 1001 --shell /bin/bash --create-home patrick
USER patrick

WORKDIR /home/patrick
RUN mkdir /home/patrick/src
WORKDIR /home/patrick/src

ENV PATH="/home/patrick/.local/bin/:$PATH"
COPY --chown=patrick:users . /home/patrick/src/

ENV LANG=C.UTF-8

CMD [ "python", "api.py" ]
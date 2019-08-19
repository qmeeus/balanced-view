FROM python:3.6-slim-stretch

COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get install -y python3-pip python3-dev git \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

# Did not find a way to use build_arg with heroku
RUN useradd --uid 1001 --shell /bin/bash --create-home patrick
USER patrick

WORKDIR /home/patrick
RUN mkdir /home/patrick/src
WORKDIR /home/patrick/src

ENV PATH="/home/patrick/.local/bin/:$PATH"
COPY --chown=patrick:users app /home/patrick/src/app

ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY --chown=patrick:users entrypoint.sh /home/patrick/src/entrypoint.sh
# Cannot use ENTRYPOINT with heroku
CMD [ "./entrypoint.sh" ]

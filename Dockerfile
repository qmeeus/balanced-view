FROM ubuntu:latest

RUN apt-get update \
    && apt-get install -y python3-pip python3-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip

ARG user_id
RUN useradd --uid $user_id --shell /bin/bash --create-home patrick
USER patrick

WORKDIR /home/patrick
RUN mkdir /home/patrick/app
WORKDIR /home/patrick/app

COPY --chown=patrick:users requirements.txt /home/patrick/app

ENV PATH="/home/patrick/.local/bin/:$PATH"
RUN pip install -r requirements.txt --user

RUN pip3 install -r requirements.txt

ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD ["flask", "run", "--host=0.0.0.0"]
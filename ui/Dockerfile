#FROM python:3.6-stretch
FROM python:3.7-alpine

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . .
# RUN apt-get update \
#     && apt-get install -y python3-pip \
#     && pip3 install --upgrade pip \
#     && pip3 install -r requirements.txt

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

CMD [ "flask", "run" ]

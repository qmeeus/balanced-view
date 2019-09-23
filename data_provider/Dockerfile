FROM python:3.7-alpine

COPY requirements.txt /
RUN pip install -r /requirements.txt

ENV USER=ui
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

COPY . .

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD [ "python", "-m", "data_provider" ]

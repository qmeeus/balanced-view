FROM python:3.7-alpine

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

CMD [ "flask", "run", "--host=0.0.0.0" ]

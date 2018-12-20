#!/bin/bash


# NB: don't forget to `heroku login` and `heroku container:login` if necessary

app="fact-checker"

heroku container:push web --app $app && \
    heroku container:release web --app $app && \
    heroku open --app $app


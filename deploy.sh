#!/bin/bash

app="fact-checker"

heroku container:push web --app $app
heroku container:release web --app $app
heroku open --app $app


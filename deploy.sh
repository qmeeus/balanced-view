#!/bin/bash

app="fact-checker"
heroku="$HOME/.local/bin/heroku/bin/heroku"

$heroku container:push web --app $app
$heroku container:release web --app $app
$heroku open --app $app


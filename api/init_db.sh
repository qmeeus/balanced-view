#!/bin/bash

if [ -d migrations ]; then
  printf "Migration folder exists. Remove? (y/N) "; read input
  if [ "$input" == "Y" ] || [ "$input" == "y" ]; then
    echo "Remove database and migrations"
    rm -r migrations
  fi
fi

if ! [ -d migrations ]; then
  flask db init
fi

flask db migrate && flask db upgrade

echo "Database updated"

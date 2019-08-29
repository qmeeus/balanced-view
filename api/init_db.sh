#!/bin/bash

DB_PATH=$(cat .env | grep SQLALCHEMY_DATABASE_NAME | cut -d= -f2)

if [ -f $DB_PATH ]; then
    echo "Database exists. Remove? y/N"; read input
    if [ "$input" == "Y" ] || [ "$input" == "y" ]; then
        echo "Remove database and migrations" 
	rm -r $DB_PATH migrations
    fi
fi

if ! [ -f $DB_PATH ]; then
    echo "Create database"
    flask db init
fi

if ! [ -d migrations ]; then
    echo "Folder migrations does not exist. Quitting..."
    exit 1
fi

flask db migrate && flask db upgrade

echo "Database updated"
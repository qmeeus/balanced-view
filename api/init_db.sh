
if [ -d /var/lib/sqlite ]; then
    DB_PATH=/var/lib/sqlite/api.db
else
    DB_PATH=../data/api.db
fi

if [ -f $DB_PATH ]; then
    echo "Database exists. Remove? y/N"; read input
    if [ "$input" == "Y" ] || [ "$input" == "y" ]; then
        echo "Recreate DB" 
	rm -r $DB_PATH migrations
	flask db init
    fi
fi

if ! [ -d migrations ]; then
    echo "Folder migrations does not exist. Quitting..."
    exit 1
fi

flask db migrate && flask db upgrade

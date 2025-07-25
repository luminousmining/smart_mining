USERNAME=luminousminer
DATABASE=smart_mining
FILE_INIT_DB=db.sql

if ! psql -U $USERNAME -lqt | cut -d \| -f 1 | grep -qw $DATABASE; then
    createdb -U $USERNAME $DATABASE
fi


psql\
 -U $USERNAME\
 -d $DATABASE\
 -f $FILE_INIT_DB

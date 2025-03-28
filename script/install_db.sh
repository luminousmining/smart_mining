USERNAME=postgres
DATABASE=smart_mining
FILE_INIT_DB=utils/db.sql

psql\
 -U $USERNAME\
 -d $DATABASE\
 -f $FILE_INIT_DB

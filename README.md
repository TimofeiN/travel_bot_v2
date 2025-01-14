### travel_bot


###
##### DOCKER
- **$ docker-compose build**  
Build the containers.
- **$ docker-compose up -d**  
Start the database in the background.  
- **$ docker-compose run --rm bot bash**  
Enter the container.
- **$ docker-compose stop**  
Stop the containers.



###
##### START, DEBUG, LINTERS
All commands are executed inside the container:


###### Bot (start / stop):
- $ python main.py
- $ Ctrl + C

###
###### Lint:
Check and format your code.  
Remove --check from black and isort for auto-formatting.
- $ isort --check .
- $ black --check .
- $ flake8

###
###### Installing / removing packages:
- $ poetry add <new_package>
- $ poetry remove <old_package>


###
##### DATABASE
###### Restore DB from dump file:
- $ docker ps   
  (find the database container ID )
- $ cd <directory_with_dump_file>
- $ docker exec -i <container_id> /usr/bin/mysql <bot_db> < dump_file.sql   

###
###### Check DB data:
- $ docker-compose exec bot-db mysql
- $ show databases;
- $ \u <bot_db_name>
- $ show tables;

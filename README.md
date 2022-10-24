# Project Mars War
A django based website to keep track of competitive DDR performance

## Getting Started
#### Prereqs
- Create a PostgreSQL database. This can be done with a standalone server or with docker
- Create a file in the root of the project called `.env` and fill it in with the following, replacing what is in angle brackets:
```
# Django secret key. Make this a long string!
SECRET_KEY=<long random string>

# Django variables
# Set to True for dev. False for production
DEBUG=True

# Database config. Change these if you are using a different DB setup
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Various API tokens
STARTGG_API_TOKEN=<API token obtained from start.gg>
LIFE4_USER=<your email used to sign it>
LIFE4_PASSWORD=<your password>

# Django admin user info
DJANGO_USER=<whatever>
DJANGO_PASSWORD=<also whatever>

# Redis config. Change this if you are using a different setup
REDIS_HOST=redis
REDIS_PORT=6379
```

#### Setting up the environment
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
```

#### Populating player data
```
python3 manage.py initiate_player_data -a -l -c 5
```
This will look for all tournaments and populate tournament, player, and match data into the database. `-a` will look for all tournaments available. The `-l` flag is if you want to include life4 data. `-c` is for display purposes only and show the rankings of people that have more than 5 matches played

```
python3 manage.py adjust_ranks -c 5
```
This will compare everyones ratings and assign a rank to players. `-c 5` is for ranking players that have more than 5 matches played.

## Deploying
If you have a server available to run things from, you can use the included `docker-compose.yml` file to do so with Docker. 
```
docker-compose up
```
This will stand up everything but does not start the HTTPS server or create the certificate. Starting the application layer can take some time so be patient for the site to load up. Follow the logs to see its progress with `docker-compose logs -f web`. While django populates player data, create the cert in another session

#### Certificate creation
Next we will need to create a certificate to enable the HTTPS portion of the server. Replace the angle bracket part with your website name:
```
docker-compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d <example.org>
```
This will get a cert and put it in the location that nginx will look for. After this is done, open up the `nginx.conf` and uncomment the HTTPS portion of the config. Then, restart the nginx container.
```
docker-compose restart nginx
```
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
DB_HOST=localhost
DB_PORT=5432

# Various API tokens
STARTGG_API_TOKEN=<API token obtained from start.gg>
LIFE4_USER=<your email used to sign it>
LIFE4_PASSWORD=<your password>
```

#### Setting up the environment
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
```
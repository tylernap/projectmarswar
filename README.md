# Project Mars War
A django based website to keep track of competitive DDR performance

## Getting Started
#### Prereqs
- Create a PostgreSQL database. This can be done with a standalone server or with docker
- Update `projectmarswar/settings` and edit the `DATABASE` settings with your PostgreSQL server information
- Create a file in the root of the project called `.env` and fill it in with the following, replacing what is in angle brackets:
```
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
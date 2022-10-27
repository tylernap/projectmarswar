import challonge
import environ

env = environ.Env()
challonge.set_credentials(env("CHALLONGE_USERNAME"), env("CHALLONGE_API_TOKEN"))
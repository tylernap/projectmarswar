import challonge
import environ


env = environ.Env()
challonge.set_credentials(env("CHALLONGE_USERNAME"), env("CHALLONGE_API_TOKEN"))


def get_tournament(tournament: str) -> dict:
    return challonge.tournaments.show(tournament)


def get_players(tournament: str) -> dict:
    return challonge.participants.index(tournament)


def get_matches(tournament: str) -> dict:
    return challonge.matches.index(tournament)
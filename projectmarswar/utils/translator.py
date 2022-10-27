from datetime import datetime, timezone
from typing import Tuple

from projectmarswar.models import Bracket, Player, Match, Tournament


def create_tournament(source: str, tournament: dict) -> Tuple:
    if source == "startgg":
        tournament_tuple = _create_startgg_tournament(tournament)
    else:
        return UnsupportedSourceType(f"Source type {source} is not supported")

    return tournament_tuple


def create_bracket(source: str, bracket: dict, event_name: str, tournament: Tournament) -> Tuple:
    if source == "startgg":
        bracket_tuple = _create_startgg_bracket(bracket, event_name, tournament)
    else:
        return UnsupportedSourceType(f"Source type {source} is not supported")

    return bracket_tuple


def create_player(source: str, player: dict) -> Tuple:
    if source == "startgg":
        player_tuple = _create_startgg_player(player)
    else:
        return UnsupportedSourceType(f"Source type {source} is not supported")

    return player_tuple


def create_match(source: str, match: dict, bracket: Bracket) -> Tuple:
    if source == "startgg":
        match_tuple = _create_startgg_match(match, bracket)
    else:
        return UnsupportedSourceType(f"Source type {source} is not supported")

    return match_tuple


def _create_startgg_tournament(tournament: dict) -> Tuple:
    return Tournament.objects.get_or_create(
        id=tournament["tournamentId"],
        name=tournament["tournamentName"],
        slug=tournament["tournamentSlug"],
        type="SG",
        date=datetime.fromtimestamp(int(tournament["startAt"]), tz=timezone.utc)
    )


def _create_startgg_bracket(bracket: dict, event_name: str, tournament: Tournament) -> Tuple:
    return Bracket.objects.get_or_create(
        id=bracket,
        event_name=event_name,
        # TODO: Change this to get the actual bracket name
        name=event_name,
        tournament=tournament
    )


def _create_startgg_player(player: dict) -> Tuple:
    return Player.objects.get_or_create(
        id=player["entrantPlayers"][0]["playerId"],
        name=player["entrantPlayers"][0]["playerTag"],
    )


def _create_startgg_match(match: dict, bracket: Bracket) -> Tuple:
    # Determine winner
    if match["winnerId"] == match["entrant1Id"]:
        winner_id = match["entrant1Players"][0]["playerId"]
    elif match["winnerId"] == match["entrant2Id"]:
        winner_id = match["entrant2Players"][0]["playerId"]
    # If winner is not set, use the greater of the scores. Otherwise call it a draw
    elif match["entrant1Score"] == match["entrant2Score"]:
        # Ideally no one should have an ID of 0
        winner_id = 0
    else:
        winner_id = max(
            match["entrant1Score"], match["entrant2Score"]
        )

    return Match.objects.get_or_create(
        id=match["id"],
        bracket=bracket,
        player1=Player.objects.get(id=match["entrant1Players"][0]["playerId"]),
        player2=Player.objects.get(id=match["entrant2Players"][0]["playerId"]),
        player1_score=match["entrant1Score"],
        player2_score=match["entrant2Score"],
        winner=Player.objects.get(id=winner_id)
    )


class UnsupportedSourceType(Exception):
    pass
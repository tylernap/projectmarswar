from datetime import datetime, timezone
import json
import os
from typing import Tuple

from projectmarswar.models import Bracket, Player, Match, Tournament


def create_tournament(source: str, tournament: dict) -> Tuple:
    if source == "startgg":
        tournament_tuple = _create_startgg_tournament(tournament)
    elif source == "challonge":
        tournament_tuple = _create_challonge_tournament(tournament)
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
    elif source == "challonge":
        player_tuple = _create_challonge_player(player)
    else:
        return UnsupportedSourceType(f"Source type {source} is not supported")

    return player_tuple


def create_match(source: str, match: dict, bracket: Bracket) -> Tuple:
    if source == "startgg":
        match_tuple = _create_startgg_match(match, bracket)
    elif source == "challonge":
        match_tuple = _create_challonge_match(match, bracket)
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
    # Skip matches that are not complete
    if not match["completed"]:
        return None, False
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


def _create_challonge_tournament(tournament: dict) -> Tuple:
    # Just don't bother with the absolute disaster of unfinished tournaments    
    if tournament["state"] != "complete":
        return None, False
    return Tournament.objects.get_or_create(
        id=tournament["id"],
        name=tournament["name"],
        slug=tournament["url"],
        type="CH",
        date=tournament["started_at"]
    )


def _create_challonge_player(player: dict) -> Tuple:
    return Player.objects.get_or_create(
        id=player["id"],
        name=player["name"],
    )


def _create_challonge_match(match: dict, bracket: Bracket) -> Tuple:
    # Skip matches that are not complete
    if match["state"] != "complete":
        return None, False
    scores = match["scores_csv"].split("-")
    return Match.objects.get_or_create(
        id=match["id"],
        bracket=bracket,
        player1=Player.objects.get(id=match["player1_id"]),
        player2=Player.objects.get(id=match["player2_id"]),
        player1_score=scores[0],
        player2_score=scores[1],
        winner=Player.objects.get(id=match["winner_id"])
    )


def translate_name(name: str) -> str:
    translation_content = {}
    translation_file = os.path.join(os.path.dirname(__file__), "name_translation.json")
    if os.path.exists(translation_file):
        with open(translation_file) as f:
            translation_content = json.load(f)
        for player, translated_list in translation_content.items():
            for translated_name in translated_list:
                if translated_name.lower() == name.lower():
                    return player
        return name
    else:
        raise Exception("name_translation.json does not exist")


class UnsupportedSourceType(Exception):
    pass
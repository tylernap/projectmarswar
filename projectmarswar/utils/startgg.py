from datetime import datetime, timezone
import os
import time
from typing import Callable

import environ
import pysmashgg


env = environ.Env()
API_TOKEN = env("STARTGG_API_TOKEN")
smash = pysmashgg.SmashGG(API_TOKEN, True)

# TODO: These game IDs were obtained manually through a graphql query to start.gg
# This could probably be automated at some point, but for now...
DDR_A_ID = 2902
DDR_A20_NOSPACE_ID = 33637
DDR_A20_ID = 34558
DDR_A3_ID = 44865
DDR_EXTREME_PRO_ID = 2907

# When searching for all tournaments, these IDs will be the ones searched
GAMES_TO_SEARCH = [
    DDR_A_ID,
    DDR_A20_ID,
    DDR_A20_NOSPACE_ID,
    DDR_EXTREME_PRO_ID,
]

# Filter all tournaments by minimum number of entrants
MIN_NUM_OF_ENTRANTS = 20

# Include these tournaments
NAME_INCLUDE_FILTER = ["Dance Dance Revolution", "DanceDanceRevolution", "DDR"]
# Exclude these tournaments
NAME_EXCLUDE_FILTER = ["Freestyle", "freestyle"]

# Retries if a call falls
RETRY_AMOUNT = 3
# Wait time between retries in seconds
RETRY_TIME = 1


def paginate(function: Callable, *args) -> list:
    """
    A helper function to help us paginate through start.gg responses
    """
    results = []
    page_number = 1
    while True:
        for retry in range(1, RETRY_AMOUNT):
            try:
                page = function(*args, page_number)
                if not page:
                    return results
                results += page
                break
            except TypeError as e:
                if retry == RETRY_AMOUNT:
                    print(f"Failed to return results: {str(e)}")
                    break
                print(f"Failed to return results: {str(e)}. Retrying in {RETRY_TIME} seconds")
                time.sleep(RETRY_TIME)
        page_number += 1


def get_all_tournaments() -> list:
    tournaments = []
    for game in GAMES_TO_SEARCH:
        tournaments += paginate(
            smash.tournament_show_event_by_game_size_dated,
            MIN_NUM_OF_ENTRANTS,
            game,
            0,
            int(time.time()),
        )
    return tournaments


def get_tournament(slug: str) -> dict:
    info = smash.tournament_show(slug)
    return {
        "tournamentName": info["name"],
        "tournamentId": info["id"],
        "tournamentSlug": slug,
        "startAt": info["startTimestamp"]
    }


def get_brackets_from_tournament(tournament) -> list:
    for retry in range(1, RETRY_AMOUNT):
        try:
            events = smash.tournament_show_all_event_brackets(tournament.slug)
        except TypeError as e:
            if retry == RETRY_AMOUNT:
                print(f"Failed to return results: {str(e)}")
                break
            print(f"Failed to return results. Retrying in {RETRY_TIME} seconds")
            time.sleep(RETRY_TIME)

    brackets = []
    for event in events:
        if any(x in event["eventName"] for x in NAME_INCLUDE_FILTER) and not any(
            x in event["eventName"] for x in NAME_EXCLUDE_FILTER
        ):
            brackets.append((event["bracketIds"], event["eventName"]))

    return brackets


def get_players_from_bracket(bracket: str) -> list:
    return paginate(smash.bracket_show_entrants, bracket)


def get_matches_from_bracket(bracket: str) -> list:
    return paginate(smash.bracket_show_sets, bracket)

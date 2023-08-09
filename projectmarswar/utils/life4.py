import json
import os

import environ
import requests
from requests.auth import HTTPBasicAuth

RANKS_TO_IMAGE = {
    # Copper
    "Copper (P)": "w1",
    "Copper I": "w1",
    "Copper II": "w2",
    "Copper III": "w3",
    "Copper IV": "w4",
    "Copper V": "w5",
    # Bronze
    "Bronze (P)": "b1",
    "Bronze I": "b1",
    "Bronze II": "b2",
    "Bronze III": "b3",
    "Bronze IV": "b4",
    "Bronze V": "b5",
    # Silver
    "Silver (P)": "s1",
    "Silver I": "s1",
    "Silver II": "s2",
    "Silver III": "s3",
    "Silver IV": "s4",
    "Silver V": "s5",
    # Gold
    "Gold III (P)": "g1",
    "Gold I": "g1",
    "Gold II": "g2",
    "Gold III": "g3",
    "Gold IV": "g4",
    "Gold V": "g5",
    # Platinum
    "Platinum (P)": "p1",
    "Platinum I": "p1",
    "Platinum II": "p2",
    "Platinum III": "p3",
    "Platinum IV": "p4",
    "Platinum V": "p5",
    # Diamond
    "Diamond (P)": "d1",
    "Diamond I": "d1",
    "Diamond II": "d2",
    "Diamond III": "d3",
    "Diamond IV": "d4",
    "Diamond V": "d5",
    # Cobalt
    "Cobalt (P)": "c1",
    "Cobalt I": "c1",
    "Cobalt II": "c2",
    "Cobalt III": "c3",
    "Cobalt IV": "c4",
    "Cobalt V": "c5",
    # Pearl
    "Pearl (P)": "l1",
    "Pearl I": "l1",
    "Pearl II": "l2",
    "Pearl III": "l3",
    "Pearl IV": "l4",
    "Pearl V": "l5",
    # Amethyst
    "Amethyst (P)": "a1",
    "Amethyst I": "a1",
    "Amethyst II": "a2",
    "Amethyst III": "a3",
    "Amethyst IV": "a4",
    "Amethyst V": "a5",
    # Emerald
    "Emerald (P)": "e1",
    "Emerald I": "e1",
    "Emerald II": "e2",
    "Emerald III": "e3",
    "Emerald IV": "e4",
    "Emerald V": "e5",
    # Onyx
    "Onyx (P)": "o1",
    "Onyx I": "o1",
    "Onyx II": "o2",
    "Onyx III": "o3",
    "Onyx IV": "o4",
    "Onyx V": "o5",
}

env = environ.Env()

LIFE4_USER = env("LIFE4_USER")
LIFE4_PASSWORD = env("LIFE4_PASSWORD")

RANK_TO_RATINGS = {
    "Copper": 200,
    "Bronze": 400,
    "Silver": 600,
    "Gold": 800,
    "Platinum": 1000,
    "Diamond": 1200,
    "Cobalt": 1400,
    "Pearl": 1600,
    "Amethyst": 1800,
    "Emerald": 2000,
    "Onyx": 2200
}

class Life4:
    def __init__(self):
        self.data = self._get_life4_data()

    def _get_life4_data(self):
        try:
            auth = HTTPBasicAuth(LIFE4_USER, LIFE4_PASSWORD)
            response = requests.get("https://life4ddr.com/api/v1/rankings", auth=auth)
            if response.status_code != 200:
                raise Life4Exception(f"Failed to get Life4 data: {response.json()['message']}")
            data = response.json()["data"]
        except Life4Exception:
            # Check for local data
            try:
                module_dir = os.path.dirname(__file__)
                file_path = os.path.join(module_dir, "localdata.json")
                with open(file_path, "r") as f:
                    data = json.loads(f.readlines()[0])["data"]
            except FileNotFoundError:
                raise Life4Exception("Cannot get Life4 data and no localdata.json file is present")

        return data

    def get_player_rank(self, name):
        translation_content = {}
        translation_file = os.path.join(os.path.dirname(__file__), "name_translation.json")
        # Match up mismatched names
        if os.path.exists(translation_file):
            with open(translation_file) as f:
                translation_content = json.load(f)
        translated_names = translation_content.get(name, [name])
        for player in self.data:
            for translated_name in translated_names:
                if player["username"].lower() == translated_name.lower():
                    return player.get("rank", None)
            if player["username"].lower() == name.lower():
                return player.get("rank", None)

        return None

    def get_rating_from_rank(self, rank):
        # Initial rating is only split up by major rank
        return RANK_TO_RATINGS.get(rank.split()[0], None)

    def get_image_from_rank(self, rank):
        return RANKS_TO_IMAGE.get(rank, None)


class Life4Exception(Exception):
    pass
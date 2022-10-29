import re

from tabulate import tabulate
from django.core.management.base import BaseCommand

from projectmarswar.models import Bracket, Player, Match, Tournament
from projectmarswar.utils import challonge, startgg, life4, translator


class Command(BaseCommand):
    help = "Initiates player rankings based on previous tournaments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            "-c",
            type=int,
            help="Only show players with a minimum number of plays",
            default=0
        )
        parser.add_argument(
            "--tournaments",
            "-t",
            type=str,
            help="Comma-separated list of challonge tournaments to scan"
        )
        parser.add_argument(
            "--life4",
            "-l",
            action="store_true",
            help="Include Life4 data"
        )

    def handle(self, *args, **options):

        L4 = life4.Life4()

        def init_challonge_data():
            if options["tournaments"]:
                self.stdout.write("Getting brackets from Challonge")
                tournament_slugs = options["tournaments"].split(",")
                for slug in tournament_slugs:
                    tournament = challonge.get_tournament(slug)
                    tournament_obj, created = translator.create_tournament("challonge", tournament)
                    if created:
                        self.stdout.write(f"Created tournament {str(tournament_obj)}")
                for tournament in Tournament.objects.filter(type="CH"):
                    # Challonge does not have brackets and does not differentiate between pools
                    bracket_obj, created = Bracket.objects.get_or_create(
                        id=tournament.id,
                        event_name=tournament.name,
                        name=tournament.name,
                        tournament=tournament
                    )
                    if created:
                        self.stdout.write(f"Created bracket {str(bracket_obj)}")

                    # Keep track of players that are duplicates
                    # {Player: challonge_id}
                    player_duplicates = {}
                    # Create challonge player objects
                    players = challonge.get_players(tournament.slug)
                    for player in players:
                        # Trim off fat the organizers may put at the beginning
                        player["name"] = re.sub(r'^\d+\s+', '', player["name"])
                        # Check to see if there are any variants on the name
                        player_name = translator.translate_name(player["name"])
                        player_filter = Player.objects.filter(name__iexact=player_name)
                        if player_filter:
                            if player_duplicates.get(player_filter[0]):
                                player_duplicates[player_filter[0]].append(player["id"])
                            else:
                                player_duplicates[player_filter[0]] = [player["id"]]
                            player["name"] = player_filter[0].name
                            player["id"] = player_filter[0].id
                        player_obj, created = translator.create_player("challonge", player)
                        if created:
                            self.stdout.write(f"Created player {str(player_obj)}")
                            l4_rank = L4.get_player_rank(player_obj.name)
                            if l4_rank and options["life4"]:
                                player_obj.life4_rank = l4_rank
                                player_obj.rating = L4.get_rating_from_rank(l4_rank)
                                player_obj.save()

                    # Create match objects
                    matches = challonge.get_matches(tournament.slug)

                    for match in matches:
                        # Override player IDs if it is from a duplicate player
                        for player, challonge_ids in player_duplicates.items():
                            for challonge_id in challonge_ids:
                                if challonge_id == match["player1_id"]:
                                    if match["winner_id"] == challonge_id:
                                        match["winner_id"] = player.id
                                    elif match["loser_id"] == challonge_id:
                                        match["loser_id"] = player.id
                                    match["player1_id"] = player.id
                                if challonge_id == match["player2_id"]:
                                    if match["winner_id"] == challonge_id:
                                        match["winner_id"] = player.id
                                    elif match["loser_id"] == challonge_id:
                                        match["loser_id"] = player.id
                                    match["player2_id"] = player.id
                        match_obj, created = translator.create_match("challonge", match, bracket_obj)
                        if created:
                            self.stdout.write(f"Created match {str(match_obj)}")



        def init_startgg_data():
            # Make Tournament objects
            self.stdout.write("Getting brackets from all available tournaments from start.gg")
            tournaments = startgg.get_all_tournaments()
            for tournament in tournaments:
                tournament_obj, created = translator.create_tournament("startgg", tournament)
                if created:
                    self.stdout.write(f"Created tournament {str(tournament_obj)}")

            # Make Bracket objects
            for tournament in Tournament.objects.filter(type="SG"):
                for brackets, event_name in startgg.get_brackets_from_tournament(tournament):
                    for bracket in brackets:
                        bracket_obj, created = translator.create_bracket(
                            "startgg", bracket, event_name, tournament
                        )
                        if created:
                            self.stdout.write(f"Created bracket {str(bracket_obj)}")

            # Make Player objects from brackets
            brackets = Bracket.objects.filter(tournament__type="SG")
            self.stdout.write("Getting players from all brackets")

            for bracket in brackets:
                for player in startgg.get_players_from_bracket(bracket.id):
                    l4_rank = L4.get_player_rank(player["entrantPlayers"][0]["playerTag"])
                    player_obj, created = translator.create_player("startgg", player)
                    if created:
                        self.stdout.write(f"Created player {str(player_obj)}")
                        if l4_rank and options["life4"]:
                            player_obj.life4_rank = l4_rank
                            player_obj.rating = L4.get_rating_from_rank(l4_rank)
                            player_obj.save()

            # Make Match objects
            self.stdout.write("Getting all start.gg matches")
            self.stdout.write(self.style.WARNING("NOTE: This will take a while"))
            for bracket in brackets:
                for match in startgg.get_matches_from_bracket(bracket.id):
                    match_obj, created = translator.create_match("startgg", match, bracket)
                    if created:
                        self.stdout.write(
                            f"Created match {str(match_obj)}"
                        )

        # Check if data exists
        if (
            len(Player.objects.all()) > 0
            and len(Bracket.objects.all()) > 0
            and len(Match.objects.all()) > 0
        ):
            self.stdout.write(
                self.style.NOTICE("Data already exists. If you want to update, use purge_player_data and retry")
            )
        else:
            init_startgg_data()
            init_challonge_data()

            # Assuming match IDs are roughly chronological
            matches = Match.objects.order_by("bracket__tournament__date", "id")
            for match in matches:
                match.adjust_player_ratings()

        filtered_players = []
        for player in Player.objects.order_by("-rating"):
            if player.get_total_matches() > options["count"]:
                filtered_players.append(player)

        table = [
            [
                rank,
                player.name,
                round(player.rating),
                (
                    f"{player.wins}-{player.losses}-{player.draws} "
                    f"({player.get_record_percentage()}%)"
                ),
            ]
            for rank, player in enumerate(
                filtered_players,
                start=1,
            )
        ]
        self.stdout.write(tabulate(table, headers=["Rank", "Name", "Rating", "Record"]))
        self.stdout.write(self.style.SUCCESS("Player data has been initialized"))
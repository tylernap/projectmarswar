import re

from django.core.management.base import BaseCommand

from projectmarswar.models import Bracket, Player, Tournament
from projectmarswar.utils import life4, startgg, translator


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

        if options["tournaments"]:
            tournament_slugs = options["tournaments"].split(",")
            # Make Tournament objects
            self.stdout.write("Getting brackets from all available tournaments from start.gg")
            for slug in tournament_slugs:
                tournament_info = startgg.get_tournament(slug)
                tournament, created = translator.create_tournament("startgg", tournament_info)
                if created:
                    self.stdout.write(f"Created tournament {str(tournament)}")

                for brackets, event_name in startgg.get_brackets_from_tournament(tournament):
                    for bracket in brackets:
                        bracket_obj, created = translator.create_bracket(
                            "startgg", bracket, event_name, tournament
                        )
                        if created:
                            self.stdout.write(f"Created bracket {str(bracket_obj)}")

                # Make Player objects from brackets
                brackets = Bracket.objects.filter(tournament=tournament)
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
                self.stdout.write("Getting matches")
                for bracket in brackets:
                    for match in startgg.get_matches_from_bracket(bracket.id):
                        match_obj, created = translator.create_match("startgg", match, bracket)
                        if created:
                            self.stdout.write(
                                f"Created match {str(match_obj)}"
                            )
        else:
            self.stdout.write(self.style.ERROR("No tournaments provided. Use -t"))
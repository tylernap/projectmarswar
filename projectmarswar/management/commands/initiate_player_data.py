from datetime import datetime, timezone
import time

from tabulate import tabulate
from django.core.management.base import BaseCommand, CommandError

from projectmarswar.models import Bracket, Player, Match, Tournament
from projectmarswar.utils import startgg, life4, translator


class Command(BaseCommand):
    help = "Initiates player rankings based on previous tournaments"

    def add_arguments(self, parser):
        parser.add_argument("--all", "-a", action="store_true", help="Lookup all DDR tournaments possible")
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
            help="Comma-separated list of tournaments to scan. Minimum 2 tournaments"
        )
        parser.add_argument(
            "--life4",
            "-l",
            action="store_true",
            help="Include Life4 data"
        )

    def handle(self, *args, **options):

        def init_startgg_data():
            # Make Tournament objects
            if options["all"]:
                self.stdout.write("Getting brackets from all available tournaments from start.gg")
                tournaments = startgg.get_all_tournaments()
                for tournament in tournaments:
                    tournament_obj, created = translator.create_tournament("startgg", tournament)
                    if created:
                        self.stdout.write(f"Created tournament {str(tournament_obj)}")
            elif options["tournaments"]:
                tournament_slugs = options["tournaments"].split(",")
                if len(tournaments) <= 1:
                    raise CommandError("Tournaments option cannot be parsed or is less than 2")
                all_tournaments = startgg.get_all_tournaments()
                for slug in tournament_slugs:
                    for tournament in all_tournaments:
                        if tournament["tournamentSlug"] == slug:
                            tournament_obj, created = translator.create_tournament(
                                "startgg",
                                tournament,
                            )
                            if created:
                                self.stdout.write(f"Created tournament {str(tournament_obj)}")
            else:
                raise CommandError(
                    "No tournaments to scan. Use -a for all or -t and specify which tournaments to scan"
                )

            # Make Bracket objects
            for tournament in Tournament.objects.all():
                for brackets, event_name in startgg.get_brackets_from_tournament(tournament):
                    for bracket in brackets:
                        bracket_obj, created = translator.create_bracket(
                            "startgg", bracket, event_name, tournament
                        )
                        if created:
                            self.stdout.write(f"Created bracket {str(bracket_obj)}")

            # Make Player objects from brackets
            brackets = Bracket.objects.all()
            self.stdout.write("Getting players from all brackets")
            l4 = life4.Life4()

            for bracket in brackets:
                for player in startgg.get_players_from_bracket(bracket.id):
                    l4_rank = l4.get_player_rank(player["entrantPlayers"][0]["playerTag"])
                    player_obj, created = translator.create_player("startgg", player)
                    if created:
                        self.stdout.write(f"Created player {str(player_obj)}")
                        if l4_rank and options["life4"]:
                            player_obj.life4_rank = l4_rank
                            player_obj.rating = l4.get_rating_from_rank(l4_rank)
                            player_obj.save()

            # Make Match objects
            self.stdout.write("Getting all matches")
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
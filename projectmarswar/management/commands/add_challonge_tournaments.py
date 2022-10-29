import re

from django.core.management.base import BaseCommand

from projectmarswar.models import Bracket, Player, Tournament
from projectmarswar.utils import challonge, life4, translator


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
                # {Player: [challonge_id]}
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
        else:
            self.stdout.write(self.style.ERROR("No tournaments provided. Use -t"))
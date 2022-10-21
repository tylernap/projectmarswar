from django.core.management.base import BaseCommand

from projectmarswar.models import Player


class Command(BaseCommand):
    help = "Adjust ranks of players"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            "-c",
            type=int,
            help="Only adjust players with a minimum number of plays",
            default=0
        )

    def handle(self, *args, **options):
        players = Player.objects.order_by("-rating")
        filtered_players = [
            player for player in players if player.get_total_matches() > options["count"]
        ]
        last_rating_match = (0, 0)
        for rank, player in enumerate(filtered_players, start=1):
            if player.rating == last_rating_match[1]:
                rank = last_rating_match[0]
            else:
                last_rating_match = (rank, player.rating)
            player.rank = rank
            player.save()            
        
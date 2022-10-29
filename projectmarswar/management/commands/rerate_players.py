from django.core.management.base import BaseCommand

from projectmarswar.models import Player, Match
from projectmarswar.utils import life4


class Command(BaseCommand):
    help = "Rerates all players"

    def add_arguments(self, parser):
        parser.add_argument(
            "--life4",
            "-l",
            action="store_true",
            help="Include Life4 data"
        )

    def handle(self, *args, **options):

        L4 = life4.Life4()

        # Reset players to default rating and record
        players = Player.objects.all()
        players.update(rating=1000, wins=0, losses=0, draws=0)

        # Set ratings based on life4 if specified
        if options["life4"]:
            for player in players:
                l4_rank = L4.get_player_rank(player.name)
                if l4_rank:
                    player.life4_rank = l4_rank
                    player.rating = L4.get_rating_from_rank(l4_rank)
                player.save()
        
        matches = Match.objects.order_by("bracket__tournament__date", "id")
        matches.update(adjusted=False)
        for match in matches:
            match.adjust_player_ratings()

        self.stdout.write(self.style.SUCCESS("Player ratings have been rerated"))

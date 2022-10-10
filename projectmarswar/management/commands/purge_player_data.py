from django.core.management.base import BaseCommand, CommandError

from projectmarswar.models import Bracket, Player, Match


class Command(BaseCommand):
    help = "Clears out all player data from the database"

    def handle(self, *args, **options):
        Match.objects.all().delete()
        Player.objects.all().delete()
        Bracket.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleted all player data from database"))
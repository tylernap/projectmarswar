from itertools import chain
import math

from django.utils import timezone
from django.db import models


K_FACTOR = 64
SCALE_FACTOR = 400

class Tournament(models.Model):
    CHOICES = [
        ("SG", "Start.gg")
    ]
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    type = models.CharField(max_length=2, choices=CHOICES)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def get_brackets(self):
        return Bracket.objects.filter(tournament=self)

    def get_players(self):
        players = []
        for bracket in self.get_brackets():
            for player in bracket.get_players():
                players.append(player)

        return list(set(players))


class Bracket(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    event_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tournament.name}: {self.id}"

    def get_matches(self):
        return Match.objects.filter(bracket=self)

    def get_players(self):
        matches = self.get_matches()
        return list(set(
            [match.player1 for match in matches]
            + [match.player2 for match in matches]
        ))
    
    def get_player_count(self):
        return len(self.get_players())


class Player(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=64)
    rating = models.IntegerField(default=1000)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    rank = models.IntegerField(default=-1)
    life4_rank = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_total_matches(self):
        return self.wins + self.losses + self.draws

    def get_record_percentage(self):
        return int(100 * ((self.wins + self.draws / 2) / (self.get_total_matches())))

    def get_matches(self):
        # This looks like a nightmare but I promise it works out in the end
        return list(set(list(chain(
            Match.objects.filter(player1=self), Match.objects.filter(player2=self)
        ))))

    def get_tournaments_entered(self):
        return list(set(
            [
                match.bracket.get_tournament_name() for match in self.get_matches()
            ]
        ))


class Match(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    bracket = models.ForeignKey(Bracket, on_delete=models.CASCADE)
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player1")
    player1_rating = models.IntegerField(null=True, blank=True)
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player2")
    player2_rating = models.IntegerField(null=True, blank=True)
    player1_score = models.IntegerField()
    player2_score = models.IntegerField()
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="winner")
    rating_change = models.IntegerField(default=0)
    adjusted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}: {self.player1.name} vs {self.player2.name}"

    def adjust_player_ratings(self):
        # If for whatever reason a player is not set, just skip
        if self.player1 is None or self.player2 is None:
            return

        # If this match's score is already adjusted, skip
        if self.adjusted:
            return

        # Saving these for historical purposes
        self.player1_rating = self.player1.rating
        self.player2_rating = self.player2.rating

        player1_expected_score = 1 / (
            1 + math.pow(10, (self.player2.rating - self.player1.rating) / SCALE_FACTOR)
        )
        player2_expected_score = 1 / (
            1 + math.pow(10, (self.player1.rating - self.player2.rating) / SCALE_FACTOR)
        )

        if self.winner == self.player1:
            self.rating_change = K_FACTOR * (1 - player1_expected_score)
            self.player1.rating = self.player1.rating + (
                K_FACTOR * (1 - player1_expected_score)
            )
            self.player2.rating = self.player2.rating + (
                K_FACTOR * (0 - player2_expected_score)
            )
            self.player1.wins += 1
            self.player2.losses += 1
        elif self.winner == self.player2:
            self.rating_change = K_FACTOR * (1 - player2_expected_score)
            self.player1.rating = self.player1.rating + (
                K_FACTOR * (0 - player1_expected_score)
            )
            self.player2.rating = self.player2.rating + (
                K_FACTOR * (1 - player2_expected_score)
            )
            self.player1.losses += 1
            self.player2.wins += 1
        # Ideally, this should never happen, but adding it anyway just in case
        elif self.winner == None:
            self.player1.rating = self.player1.rating + (
                K_FACTOR * (0.5 - player1_expected_score)
            )
            self.player2.rating = self.player2.rating + (
                K_FACTOR * (0.5 - player2_expected_score)
            )
            self.player1.draws += 1
            self.player2.draws += 1

        self.adjusted = True
        self.player1.save()
        self.player2.save()
        self.save()
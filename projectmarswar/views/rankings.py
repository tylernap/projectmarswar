from django.shortcuts import render

from projectmarswar.models import Player
from projectmarswar.utils import life4

MATCH_COUNT_CUTOFF = 5

LIFE4 = life4.Life4()


def rankings_view(request):
    players = Player.objects.order_by("rank")
    # Put unranked players at the end of the list
    filtered_players = []
    for player in players:
        if player.rank != -1:
            filtered_players.append(player)
    for player in players:
        if player.rank == -1:
            filtered_players.append(player)

    ranked_players = [
        (player, LIFE4.get_image_from_rank(player.life4_rank))
        for player in filtered_players
    ]
    content = {"players": ranked_players}
    return render(request, "rankings.html", content)


def player_view(request, player):
    player_obj = Player.objects.get(id=player)
    matches = sorted(player_obj.get_matches(), key=lambda match: match.id, reverse=True)
    content = {
        "player": player_obj,
        "matches": matches,
    }
    return render(request, "player.html", content)
from django.http import Http404
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
    return render(request, "players/rankings.html", content)


def player_view(request, player):
    try:
        player_obj = Player.objects.get(id=player)
    except Player.DoesNotExist:
        raise Http404("Player does not exist")
    matches = sorted(player_obj.get_matches(), key=lambda match: match.id)
    rating_data = [ 
        match.player1_rating if match.player1 == player_obj
        else match.player2_rating
        for match in matches
    ]
    rating_data.append(player_obj.rating)
    content = {
        "player": player_obj,
        "matches": matches,
        "rating_data": rating_data,
    }
    return render(request, "players/player.html", content)
from django.shortcuts import render

from projectmarswar.models import Bracket, Tournament


def tournaments_view(request):
    content = {
        "tournaments": Tournament.objects.order_by("-date")
    }
    return render(request, "tournaments/tournaments.html", content)


def tournament_details_view(request, tournament):
    content = {
        "tournament": Tournament.objects.get(id=tournament)
    }
    return render(request, "tournaments/tournament.html", content)


def bracket_details_view(request, bracket):
    conent = {
        "bracket": Bracket.objects.get(id=bracket)
    }
    return render(request, "tournaments/bracket.html", content)
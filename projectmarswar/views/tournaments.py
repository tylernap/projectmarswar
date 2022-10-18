from django.http import Http404
from django.shortcuts import render

from projectmarswar.models import Bracket, Tournament


def tournaments_view(request):
    content = {
        "tournaments": Tournament.objects.order_by("-date")
    }
    return render(request, "tournaments/tournaments.html", content)


def tournament_details_view(request, tournament):
    try:
        tournament_obj = Tournament.objects.get(id=tournament)
    except Tournament.DoesNotExist:
        raise Http404("Tournament does not exist")
    brackets = tournament_obj.get_brackets()

    content = {
        "tournament": tournament_obj,
        "brackets": brackets,
    }
    return render(request, "tournaments/details.html", content)


def bracket_details_view(request, bracket):
    content = {
        "bracket": Bracket.objects.get(id=bracket)
    }
    return render(request, "tournaments/bracket.html", content)
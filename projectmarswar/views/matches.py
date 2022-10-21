from django.http import Http404
from django.shortcuts import render

from projectmarswar.models import Match


def matches_view(request):
    content = {
        "matches": Match.objects.all()
    }
    return render(request, "matches/matches.html", content)


def match_details_view(request, match):
    try:
        match_obj = Match.objects.get(id=match)
    except Match.DoesNotExist:
        raise Http404("Match does not exist")
    content = {
        "match": match_obj,
    }
    return render(request, "matches/details.html", content)
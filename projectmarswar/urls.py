"""projectmarswar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers, serializers, viewsets

from projectmarswar import models
from projectmarswar.views import rankings, tournaments, matches


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Player
        fields = "__all__"


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = models.Player.objects.all()
    serializer_class = PlayerSerializer


class MatchSerializer(serializers.ModelSerializer):
    bracket = serializers.CharField(source="bracket.id", read_only=True)
    player1 = serializers.CharField(source="player1.id", read_only=True)
    player2 = serializers.CharField(source="player2.id", read_only=True)
    winner = serializers.CharField(source="winner.id", read_only=True)

    class Meta:
        model = models.Match
        fields = "__all__"


class MatchViewSet(viewsets.ModelViewSet):
    queryset = models.Match.objects.all()
    serializer_class = MatchSerializer


class BracketSerializer(serializers.ModelSerializer):
    tournament = serializers.CharField(source="tournament.id", read_only=True)

    class Meta:
        model = models.Bracket
        fields = "__all__"


class BracketViewSet(viewsets.ModelViewSet):
    queryset = models.Bracket.objects.all()
    serializer_class = BracketSerializer


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tournament
        fields = "__all__"


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = models.Tournament.objects.all()
    serializer_class = TournamentSerializer


router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'brackets', BracketViewSet)
router.register(r'tournaments', TournamentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('players/', rankings.rankings_view),
    path('players/<int:player>/', rankings.player_view),
    path('tournaments/', tournaments.tournaments_view),
    path('tournaments/<int:tournament>/', tournaments.tournament_details_view),
    path('matches/', matches.matches_view),
    path('matches/<int:match>/', matches.match_details_view),
    path('api-auth/', include('rest_framework.urls')),
    path('__reload__', include("django_browser_reload.urls")),
    re_path(r'^', include('cms.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
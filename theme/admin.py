from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from projectmarswar import models


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date')
    list_filter = ['date', 'type']
    search_fields = ["name"]


class BracketAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ['tournament']
    search_fields = ["name", "tournament__name"]


class RatingListFilter(admin.SimpleListFilter):
    title = _("rating level")
    parameter_name = "rating"

    def lookups(self, request, model_admin):
        return (
            ('All', _('All')),
            ('0', _('0')),
            ('500', _('500')),
            ('1000', _('1000')),
            ('1500', _('1500')),
            ('2000', _('2000')),
            ('2500', _('2500')),
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != "All":
            rating = int(self.value())
            return queryset.filter(
                rating__gte=rating,
                rating__lte=rating+499
            )
        else:
            return queryset


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating', 'rank')
    list_filter = (RatingListFilter,)
    search_fields = ["name"]


class MatchAdmin(admin.ModelAdmin):
    list_filter = ["adjusted"]
    search_fields = ["player1__name", "player2__name", "bracket__tournament__name"]



admin.site.register(models.Tournament, TournamentAdmin)
admin.site.register(models.Bracket, BracketAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Match, MatchAdmin)
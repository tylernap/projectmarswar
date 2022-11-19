from django.contrib import admin

from projectmarswar import models

admin.site.register(models.Tournament)
admin.site.register(models.Bracket)
admin.site.register(models.Player)
admin.site.register(models.Match)
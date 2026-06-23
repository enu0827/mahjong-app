from django.contrib import admin
from .models import Player, Season, Game, Result

admin.site.register(Player)
admin.site.register(Season)
admin.site.register(Game)
admin.site.register(Result)

# Register your models here.

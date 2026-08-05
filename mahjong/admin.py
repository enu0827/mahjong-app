from django.contrib import admin
from .models import Player, Season, Game, Result


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "carryover_profit",
        "carryover_game_count",
        "carryover_first_count",
        "carryover_second_count",
        "carryover_third_count",
        "carryover_fourth_count",
    )


admin.site.register(Season)
admin.site.register(Game)
admin.site.register(Result)
# Register your models here.

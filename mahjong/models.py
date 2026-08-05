from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)

    carryover_profit = models.FloatField(
        default=0,
        verbose_name="第7節までの持ち越し収支"
    )

    carryover_game_count = models.PositiveIntegerField(
        default=0,
        verbose_name="第7節までの対局数"
    )

    carryover_first_count = models.PositiveIntegerField(
        default=0,
        verbose_name="第7節までの1着回数"
    )

    carryover_second_count = models.PositiveIntegerField(
        default=0,
        verbose_name="第7節までの2着回数"
    )

    carryover_third_count = models.PositiveIntegerField(
        default=0,
        verbose_name="第7節までの3着回数"
    )

    carryover_fourth_count = models.PositiveIntegerField(
        default=0,
        verbose_name="第7節までの4着回数"
    )

    def __str__(self):
        return self.name

class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    date = models.DateField()
    game_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.season.name} {self.date} 第{self.game_number}回"


class Result(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    rank = models.IntegerField()
    score = models.IntegerField()

    profit = models.FloatField(default=0)

    def __str__(self):
        return f"{self.game} {self.player.name}"
# Create your models here.

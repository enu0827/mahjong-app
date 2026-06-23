from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    date = models.DateField()
    game_number = models.IntegerField()

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

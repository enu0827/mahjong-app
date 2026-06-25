from django import forms
from .models import Season, Player
from datetime import date


class GameResultForm(forms.Form):

    score_widget = forms.TextInput(
        attrs={
            "type": "text",
            "inputmode": "decimal",
            "autocomplete": "off",
        }
    )

    season = forms.ModelChoiceField(
        queryset=Season.objects.all(),
        label="シーズン"
    )

    date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(
            attrs={
                "type": "date"
            }
        )
    )

    player1 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        label="プレイヤー1"
    )
    score1 = forms.IntegerField(
        label="スコア",
        widget=score_widget
    )

    player2 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        label="プレイヤー2"
    )
    score2 = forms.IntegerField(
        label="スコア",
        widget=score_widget
    )

    player3 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        label="プレイヤー3"
    )
    score3 = forms.IntegerField(
        label="スコア",
        widget=score_widget
    )

    player4 = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        label="プレイヤー4"
    )
    score4 = forms.IntegerField(
        label="スコア",
        widget=score_widget
    )

    def clean(self):
        cleaned_data = super().clean()

        players = []
        scores = []

        for i in range(1, 5):
            player = cleaned_data.get(f"player{i}")
            score = cleaned_data.get(f"score{i}")

            if player:
                players.append(player)

            if score is not None:
                scores.append(score)

        # プレイヤー重複チェック
        if len(players) == 4 and len(set(players)) != 4:
            raise forms.ValidationError(
                "同じプレイヤーが選ばれています。4人すべて別のプレイヤーにしてください。"
            )

        # 合計1000チェック（250=25000点）
        if len(scores) == 4 and sum(scores) != 1000:
            raise forms.ValidationError(
                f"4人の合計点が1000になっていません。（現在 {sum(scores)}）"
            )

        return cleaned_data
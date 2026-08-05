from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg
from datetime import date as dt_date
from .models import Game, Result, Season, Player
from .forms import GameResultForm
import json
from django.contrib.auth.decorators import login_required

UMA = {
    1: 50,
    2: 10,
    3: -10,
    4: -30,
}

@login_required
def home(request):
    today = dt_date.today()

    today_results = (
        Result.objects
        .filter(game__date=today)
        .values("player__name")
        .annotate(
            total_profit=Sum("profit"),
            game_count=Count("id"),
            average_rank=Avg("rank"),
        )
        .order_by("-total_profit")
    )

    today_list = []

    for player in today_results:
        player["money"] = player["total_profit"] * 50
        today_list.append(player)

    today_game_count = Game.objects.filter(date=today).count()

    return render(request, "mahjong/home.html", {
        "today_results": today_list,
        "today_game_count": today_game_count,
        "players": Player.objects.all(),
    })

@login_required
def add_game(request):
    next_game_number = 1
    season_game_count = 0

    if request.method == "POST":
        form = GameResultForm(request.POST)

        if form.is_valid():
            season = form.cleaned_data["season"]
            game_date = form.cleaned_data["date"]

            season_game_count = Game.objects.filter(
                season=season
            ).count()

            # 選択したシーズンが80戦に到達していたら、
            # 次の「第◯節」を自動作成して切り替える
            if season_game_count >= 80:
                season_name = season.name

                try:
                    season_number = int(
                        season_name
                        .replace("第", "")
                        .replace("節", "")
                    )
                    new_season_name = f"第{season_number + 1}節"

                except ValueError:
                    new_season_name = f"{season_name} 次シーズン"

                season, created = Season.objects.get_or_create(
                    name=new_season_name,
                    defaults={
                        "start_date": game_date,
                        "end_date": game_date,
                    }
                )

                season_game_count = Game.objects.filter(
                    season=season
                ).count()

            next_game_number = season_game_count + 1

            # 念のため、新しいシーズン側も80戦なら登録を止める
            if season_game_count >= 80:
                form.add_error(
                    None,
                    "次のシーズンも80戦に到達しています。"
                    "管理画面から新しいシーズンを確認してください。"
                )

                return render(
                    request,
                    "mahjong/add_game.html",
                    {
                        "form": form,
                        "next_game_number": next_game_number,
                        "season_game_count": season_game_count,
                    },
                )

            players_scores = []

            for i in range(1, 5):
                players_scores.append({
                    "player": form.cleaned_data[f"player{i}"],
                    "score": form.cleaned_data[f"score{i}"] * 100,
                })

            # プレイヤー重複チェック
            selected_players = [
                data["player"]
                for data in players_scores
            ]

            if len(selected_players) != len(set(selected_players)):
                form.add_error(
                    None,
                    "同じプレイヤーが選択されています。"
                )

                return render(
                    request,
                    "mahjong/add_game.html",
                    {
                        "form": form,
                        "next_game_number": next_game_number,
                        "season_game_count": season_game_count,
                    },
                )

            # 合計点チェック
            total_score = sum(
                data["score"]
                for data in players_scores
            )

            if total_score != 100000:
                form.add_error(
                    None,
                    f"4人の合計点が100000点ではありません。"
                    f"現在は{total_score}点です。"
                )

                return render(
                    request,
                    "mahjong/add_game.html",
                    {
                        "form": form,
                        "next_game_number": next_game_number,
                        "season_game_count": season_game_count,
                    },
                )

            # 同点チェック
            scores = [
                data["score"]
                for data in players_scores
            ]

            if len(scores) != len(set(scores)):
                form.add_error(
                    None,
                    "同点のプレイヤーがいます。"
                    "順位を自動判定できないため、点数を確認してください。"
                )

                return render(
                    request,
                    "mahjong/add_game.html",
                    {
                        "form": form,
                        "next_game_number": next_game_number,
                        "season_game_count": season_game_count,
                    },
                )

            game = Game.objects.create(
                season=season,
                date=game_date,
                game_number=next_game_number
            )

            players_scores.sort(
                key=lambda data: data["score"],
                reverse=True
            )

            for rank, data in enumerate(
                players_scores,
                start=1
            ):
                score = data["score"]

                profit = (
                    (score - 30000) / 1000
                    + UMA[rank]
                )

                Result.objects.create(
                    game=game,
                    player=data["player"],
                    rank=rank,
                    score=score,
                    profit=profit,
                )

            return redirect("game_list")

        # フォーム自体が無効だった場合も、
        # 対局番号と進捗を表示できるようにする
        season_id = request.POST.get("season")

        if season_id:
            selected_season = Season.objects.filter(
                id=season_id
            ).first()

            if selected_season:
                season_game_count = Game.objects.filter(
                    season=selected_season
                ).count()

                next_game_number = season_game_count + 1

    else:
        form = GameResultForm()

        last_game = Game.objects.order_by("-id").first()

        if last_game:
            last_season = last_game.season

            last_season_game_count = Game.objects.filter(
                season=last_season
            ).count()

            if last_season_game_count >= 80:
                season_name = last_season.name

                try:
                    season_number = int(
                        season_name
                        .replace("第", "")
                        .replace("節", "")
                    )

                    new_season_name = (
                        f"第{season_number + 1}節"
                    )

                except ValueError:
                    new_season_name = (
                        f"{season_name} 次シーズン"
                    )

                selected_season, created = Season.objects.get_or_create(
                    name=new_season_name,
                    defaults={
                        "start_date":dt_date.today(),
                        "end_date": dt_date.today(),
                    }
                )
                   

            else:
                selected_season = last_season

            season_game_count = Game.objects.filter(
                season=selected_season
            ).count()

            next_game_number = season_game_count + 1

            form.fields["season"].initial = selected_season

            # 前回の4人を引き継ぐ
            previous_results = Result.objects.filter(
                game=last_game
            ).order_by("rank")

            for i, result in enumerate(
                previous_results,
                start=1
            ):
                form.fields[f"player{i}"].initial = (
                    result.player
                )

        # 日付は当日
        form.fields["date"].initial = dt_date.today()

    return render(
        request,
        "mahjong/add_game.html",
        {
            "form": form,
            "next_game_number": next_game_number,
            "season_game_count": season_game_count,
        },
    )

def game_list(request):
    games = Game.objects.order_by("-date", "-game_number")

    return render(
        request,
        "mahjong/game_list.html",
        {
            "games": games,
        }
    )

@login_required
def season_ranking(request):
    season_id = request.GET.get("season")

    if season_id:
        season = Season.objects.get(id=season_id)
    else:
        season = Season.objects.last()

    season_game_count = Game.objects.filter(season=season).count()
    remaining_games = 80 - season_game_count

    rankings = (
        Result.objects
        .filter(game__season=season)
        .values("player__id", "player__name")
        .annotate(
            total_profit=Sum("profit"),
            game_count=Count("id"),
            average_rank=Avg("rank"),
        )
        .order_by("-total_profit")
    )

    ranking_list = []

    for player in rankings:
        player_id = player["player__id"]

        top_count = Result.objects.filter(
            game__season=season,
            player_id=player_id,
            rank=1
        ).count()

        last_count = Result.objects.filter(
            game__season=season,
            player_id=player_id,
            rank=4
        ).count()

        game_count = player["game_count"]

        player["top_rate"] = top_count / game_count * 100
        player["last_rate"] = last_count / game_count * 100
        player["avoid_last_rate"] = 100 - player["last_rate"]

        ranking_list.append(player)

    mvp_winner = ranking_list[0] if ranking_list else None

    avoid_last_winner = (
        sorted(ranking_list, key=lambda x: x["last_rate"])[0]
        if ranking_list else None
    )

    highest_score_result = (
        Result.objects
        .filter(game__season=season)
        .order_by("-score")
        .first()
    )

    # グラフ用データ
    graph_data = []

    games = Game.objects.filter(season=season).order_by("game_number")
    players = Player.objects.all()

    for player in players:
        cumulative = 0
        player_data = []
        has_result = False

        for game in games:
            result = Result.objects.filter(
                game=game,
                player=player
            ).first()

            if result:
                cumulative += result.profit
                has_result = True

            player_data.append({
                "game": game.game_number,
                "profit": cumulative,
            })

        if has_result:
            graph_data.append({
                "name": player.name,
                "data": player_data,
            })

    return render(request, "mahjong/season_ranking.html", {
        "season": season,
        "rankings": ranking_list,
        "seasons": Season.objects.all(),
        "season_game_count": season_game_count,
        "remaining_games": remaining_games,
        "avoid_last_winner": avoid_last_winner,
        "highest_score_result": highest_score_result,
        "mvp_winner": mvp_winner,
        "graph_data": json.dumps(graph_data, ensure_ascii=False),
    })


@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    results = Result.objects.filter(player=player).order_by("game__game_number")

    history_results = list(results)

    cumulative = 0
    labels = []
    profits = []

    for result in history_results:
        cumulative += result.profit
        result.cumulative_profit = cumulative

        labels.append(f"第{result.game.game_number}戦")
        profits.append(cumulative)

    game_count = len(history_results)
    total_profit = sum(r.profit for r in history_results)

    average_rank = (
        sum(r.rank for r in history_results) / game_count
        if game_count else 0
    )

    first_count = sum(1 for r in history_results if r.rank == 1)
    second_count = sum(1 for r in history_results if r.rank == 2)
    third_count = sum(1 for r in history_results if r.rank == 3)
    fourth_count = sum(1 for r in history_results if r.rank == 4)

    top_rate = first_count / game_count * 100 if game_count else 0
    last_rate = fourth_count / game_count * 100 if game_count else 0
    avoid_last_rate = 100 - last_rate if game_count else 0

    history_results.reverse()

    return render(
        request,
        "mahjong/player_detail.html",
        {
            "player": player,
            "game_count": game_count,
            "total_profit": total_profit,
            "average_rank": average_rank,
            "top_rate": top_rate,
            "last_rate": last_rate,
            "avoid_last_rate": avoid_last_rate,
            "first_count": first_count,
            "second_count": second_count,
            "third_count": third_count,
            "fourth_count": fourth_count,
            "labels": json.dumps(labels, ensure_ascii=False),
            "profits": json.dumps(profits),
            "results": history_results,
        },
    )

@login_required
def daily_summary(request):
    date = request.GET.get("date")

    games = Game.objects.all()

    if date:
        games = games.filter(date=date)

    results = Result.objects.filter(game__in=games)

    summary = (
        results
        .values("player__id", "player__name")
        .annotate(
            total_profit=Sum("profit"),
            game_count=Count("id"),
            average_rank=Avg("rank"),
        )
        .order_by("-total_profit")
    )
    for player in summary:
        player["money"] = player["total_profit"] * 50

    return render(request, "mahjong/daily_summary.html", {
        "date": date,
        "summary": summary,
    })

@login_required
def edit_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    results = Result.objects.filter(game=game).order_by("rank")
    players = Player.objects.all()

    if request.method == "POST":
        game.date = request.POST["date"]

        players_scores = []
        selected_players = []
        total_score = 0

        for result in results:
            player_id = int(request.POST[f"player_{result.id}"])
            score = int(request.POST[f"score_{result.id}"]) * 100

            selected_players.append(player_id)
            total_score += score

            players_scores.append({
                "result": result,
                "player": Player.objects.get(id=player_id),
                "score": score,
            })

        if len(selected_players) != len(set(selected_players)):
            return render(request, "mahjong/edit_game.html", {
                "game": game,
                "results": results,
                "players": players,
                "error": "同じプレイヤーが選択されています。",
            })

        if total_score != 100000:
            return render(request, "mahjong/edit_game.html", {
                "game": game,
                "results": results,
                "players": players,
                "error": f"4人の合計点が100000点ではありません。現在は{total_score}点です。",
            })

        game.save()

        players_scores.sort(key=lambda x: x["score"], reverse=True)

        for rank, data in enumerate(players_scores, start=1):
            result = data["result"]
            score = data["score"]

            result.player = data["player"]
            result.rank = rank
            result.score = score
            result.profit = (score - 30000) / 1000 + UMA[rank]
            result.save()

        return redirect("game_list")

    return render(request, "mahjong/edit_game.html", {
        "game": game,
        "results": results,
        "players": players,
    })
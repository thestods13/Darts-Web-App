
from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

app = Flask(__name__)
os.makedirs('./static/stats', exist_ok=True)

# Data storage
players = []
player_stats = {}  # Key: player, Value: detailed stats
matches = []
current_game = None
match_data = {"scores": [], "checkouts": [], "high_scores": []}

@app.route("/")
def home():
    return '''
    <h1>Darts Application</h1>
    <a href="/new-match">Start New Match</a> | <a href="/players">View Player Stats</a>
    '''

@app.route("/new-match", methods=["GET", "POST"])
def new_match():
    global current_game, players, match_data
    if request.method == "POST":
        players = request.form.getlist("players")
        current_game = request.form.get("game")
        match_data = {"scores": {player: [] for player in players}, "checkouts": [], "high_scores": {60: 0, 80: 0, 100: 0, 140: 0, 180: 0}}
        return redirect(url_for("match"))
    return '''
    <form method="POST">
        <label>Game Type:</label>
        <select name="game">
            <option value="501">501</option>
        </select>
        <label>Players:</label>
        <input type="text" name="players" placeholder="Player 1, Player 2">
        <button type="submit">Start Match</button>
    </form>
    '''

@app.route("/match", methods=["GET", "POST"])
def match():
    if request.method == "POST":
        for player in players:
            scores = request.form.getlist(f"{player}_scores")
            match_data["scores"][player].extend([int(score) for score in scores if score.isdigit()])
        return redirect(url_for("match"))

    scoreboard = "".join([f"<h3>{player}: {sum(match_data['scores'][player])}</h3>" for player in players])
    return f'''
    <h1>Match in Progress</h1>
    <form method="POST">
        {''.join([f'<label>{player}:</label> <input type="text" name="{player}_scores" placeholder="Enter scores (comma separated)"> <br>' for player in players])}
        <button type="submit">Update Scores</button>
    </form>
    {scoreboard}
    <a href="/match-summary">End Match</a>
    '''

@app.route("/match-summary", methods=["GET"])
def match_summary():
    global player_stats
    # Update player stats
    for player in players:
        scores = match_data["scores"][player]
        total_score = sum(scores)
        first_three_avg = sum(scores[:3]) / 3 if scores[:3] else 0
        overall_avg = sum(scores) / len(scores) if scores else 0

        # High scores tracking
        for high in [60, 80, 100, 140, 180]:
            match_data["high_scores"][high] += sum(1 for score in scores if score >= high)

        # Update player stats
        if player not in player_stats:
            player_stats[player] = {"total_games": 0, "total_score": 0, "first_three_avg": 0, "overall_avg": 0, "high_scores": {60: 0, 80: 0, 100: 0, 140: 0, 180: 0}}
        stats = player_stats[player]
        stats["total_games"] += 1
        stats["total_score"] += total_score
        stats["first_three_avg"] = (stats["first_three_avg"] + first_three_avg) / stats["total_games"]
        stats["overall_avg"] = (stats["overall_avg"] + overall_avg) / stats["total_games"]
        for high in [60, 80, 100, 140, 180]:
            stats["high_scores"][high] += match_data["high_scores"][high]

    # Save stats
    with open("player_stats.json", "w") as f:
        json.dump(player_stats, f)

    return '''
    <h1>Match Summary</h1>
    <a href="/players">View Player Stats</a>
    '''

@app.route("/players")
def players_page():
    player_stats_html = "".join([
        f"<h3>{player}</h3><ul><li>Games Played: {stats['total_games']}</li><li>First Three Avg: {stats['first_three_avg']}</li><li>Overall Avg: {stats['overall_avg']}</li><li>High Scores: {stats['high_scores']}</li></ul>"
        for player, stats in player_stats.items()
    ])
    return f'''
    <h1>Player Stats</h1>
    {player_stats_html}
    <a href="/">Back to Home</a>
    '''

@app.route("/generate-stats")
def generate_stats():
    # Generate a sample bar chart
    players = list(player_stats.keys())
    scores = [player_stats[player]["total_score"] for player in players]

    plt.bar(players, scores)
    plt.title("Total Scores by Player")
    plt.xlabel("Players")
    plt.ylabel("Total Scores")
    plt.savefig("./static/stats/total_scores.png")
    plt.close()

    return '''
    <h1>Stats Generated</h1>
    <img src="/static/stats/total_scores.png">
    <a href="/">Back to Home</a>
    '''

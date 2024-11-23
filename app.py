
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Game data
games = ["501", "301", "Mickey Mouse", "Footy", "Scoring Mouse Singles"]
players = []
current_game = None
scores = {}
targets = [20, 19, 18, 17, 16, 15]  # Default targets for Scoring Mouse Singles
progress = {}  # Tracks players' progress on targets

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        global current_game
        current_game = request.form.get("game")
        return redirect(url_for("player_setup"))
    return '''
    <form method="POST">
        <h1>Select Game</h1>
        <select name="game">
            <option value="501">501</option>
            <option value="301">301</option>
            <option value="Mickey Mouse">Mickey Mouse</option>
            <option value="Footy">Footy</option>
            <option value="Scoring Mouse Singles">Scoring Mouse Singles</option>
        </select>
        <button type="submit">Next</button>
    </form>
    '''

@app.route("/setup", methods=["GET", "POST"])
def player_setup():
    global players, scores, progress
    if request.method == "POST":
        players = request.form.getlist("player")
        if current_game == "Scoring Mouse Singles":
            progress = {player: {target: 0 for target in targets} for player in players}
        else:
            scores = {player: 501 if current_game == "501" else 301 for player in players}
        return redirect(url_for("scoreboard"))
    return '''
    <form method="POST">
        <h1>Enter Players</h1>
        <input type="text" name="player" placeholder="Player 1">
        <input type="text" name="player" placeholder="Player 2">
        <button type="submit">Start Game</button>
    </form>
    '''

@app.route("/scoreboard", methods=["GET", "POST"])
def scoreboard():
    global scores, progress
    if current_game == "Scoring Mouse Singles":
        if request.method == "POST":
            for player in players:
                for target in targets:
                    hits = int(request.form.get(f"{player}_{target}", 0))
                    progress[player][target] = min(progress[player][target] + hits, 3)
            return redirect(url_for("scoreboard"))
        progress_table = "<br>".join([
            f"<p>{player}: " + ", ".join([f"{target}: {progress[player][target]}/3" for target in targets]) + "</p>"
            for player in players
        ])
        return f'''
        <h1>Scoring Mouse Singles</h1>
        <form method="POST">
            {progress_table}
            {"".join([f"<p>{player}: " + "".join([f"<input type='number' name='{player}_{target}' placeholder='{target} hits'>" for target in targets]) + "</p>" for player in players])}
            <button type="submit">Update Scores</button>
        </form>
        <a href="/results">Finish Game</a>
        '''
    else:
        if request.method == "POST":
            for player in scores:
                reduction = int(request.form.get(player, 0))
                scores[player] = max(0, scores[player] - reduction)
            return redirect(url_for("scoreboard"))
        score_table = ''.join([f"<p>{player}: {score}</p>" for player, score in scores.items()])
        return f'''
        <h1>Scoreboard</h1>
        <form method="POST">
            {score_table}
            {"".join([f"<input type='number' name='{player}' placeholder='Score for {player}'>" for player in scores])}
            <button type="submit">Update</button>
        </form>
        <a href="/results">Finish Game</a>
        '''

@app.route("/results")
def results():
    global scores, progress
    if current_game == "Scoring Mouse Singles":
        winner = max(players, key=lambda player: sum(1 for target in targets if progress[player][target] == 3))
        return f'''
        <h1>Game Over</h1>
        <p>Winner: {winner}</p>
        <p>Final Progress: {progress}</p>
        <a href="/">Restart</a>
        '''
    else:
        winner = min(scores, key=scores.get)
        return f'''
        <h1>Game Over</h1>
        <p>Winner: {winner}</p>
        <p>Final Scores: {scores}</p>
        <a href="/">Restart</a>
        '''

if __name__ == "__main__":
    app.run(debug=True)

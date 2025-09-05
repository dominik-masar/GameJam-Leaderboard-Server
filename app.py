import json
import os
from flask import Flask, request, jsonify
import dash
from dash import dcc, html, dash_table
from flask_cors import CORS

# --------------------------
# Flask backend for API
# --------------------------
server = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(BASE_DIR, "scores.json")
MAX_ENTRIES = 10

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        return json.load(f)

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

def delete_data():
    os.remove(SCORES_FILE)

@server.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.json
    name = data.get("name", "Anonymous")
    score = int(data.get("score", 0))

    scores = load_scores()
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:MAX_ENTRIES]
    save_scores(scores)

    return {"status": "ok", "leaderboard": scores}

@server.route("/totally_secret_delete", methods=["GET"])
def totally_secret_delete():
    delete_data()
    return 200

@server.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(load_scores())

# --------------------------
# Dash frontend
# --------------------------
app = dash.Dash(__name__, server=server, url_base_pathname="/")
CORS(app)

app.layout = html.Div([
    html.H1("🏆 Top 10 Leaderboard"),
    dash_table.DataTable(
        id="table",
        columns=[
            {"name": "Rank", "id": "rank"},
            {"name": "Name", "id": "name"},
            {"name": "Score", "id": "score"}
        ],
        data=[
            {"rank": i+1, "name": entry["name"], "score": entry["score"]}
            for i, entry in enumerate(load_scores())
        ],
        style_cell={"textAlign": "center", "padding": "8px"},
        style_header={"backgroundColor": "#4CAF50", "color": "white", "fontWeight": "bold"},
        style_table={"margin": "auto", "width": "50%"}
    ),
    dcc.Interval(
        id="interval-component",
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    dash.Output("table", "data"),
    dash.Input("interval-component", "n_intervals")
)
def update_table(n):
    scores = load_scores()
    return [
        {"rank": i+1, "name": entry["name"], "score": entry["score"]}
        for i, entry in enumerate(scores)
    ]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

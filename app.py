from flask import Flask, request, jsonify
from models import db, Score
import os

app = Flask(__name__)

# Load the PostgreSQL URL from the environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fallback.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables when app starts (only once)
with app.app_context():
    db.create_all()


@app.route("/api/scores", methods=["GET"])
def get_scores():
    """Return all scores in descending order."""
    scores = Score.query.order_by(Score.score.desc()).all()
    return jsonify([{"name": s.name, "score": s.score} for s in scores])

@app.route("/api/submit", methods=["POST"])
def submit_score():
    """Add a new score via JSON: {name: str, score: int}"""
    data = request.get_json()
    new_score = Score(name=data["name"], score=data["score"])
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"message": "Score saved"}), 201

if __name__ == "__main__":
    app.run()

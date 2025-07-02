from flask import Flask, request, jsonify, render_template
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/api/scores", methods=["GET"])
def get_scores():
    """Return all scores in descending order."""
    scores = Score.query.order_by(Score.score.desc()).all()
    return jsonify({s.name.lower(): s.score for s in scores})

@app.route("/api/submit", methods=["POST"])
def submit_score():
    """Add a new score via JSON: {name: str, score: int}"""
    data = request.get_json()
    new_score = Score(name=data["name"], score=data["score"])
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"message": "Score saved"}), 201

@app.route("/api/update", methods=["POST"])
def update_score():
    """Update existing score"""
    data = request.get_json()
    name = data.get("person")
    change = int(data.get("change", 0))

    if not name:
        return jsonify({"error": "Name is required"}), 400

    score = Score.query.filter_by(name=name).first()

    if not score:
        # If not found, create a new one
        score = Score(name=name, score=change)
        db.session.add(score)
    else:
        score.score += change

    db.session.commit()

    # Return updated scores
    scores = Score.query.order_by(Score.score.desc()).all()
    return jsonify({s.name.lower(): s.score for s in scores})

if __name__ == "__main__":
    app.run()

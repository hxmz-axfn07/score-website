import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

SCORES_FILE = 'scores.json'

# Load scores from file or initialize them
def load_scores():
    if not os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'w') as f:
            json.dump({"ali": 0, "hamza": 0, "yasir": 0}, f)
    with open(SCORES_FILE, 'r') as f:
        return json.load(f)

# Save scores to file
def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

# REST API to get scores
@app.route('/api/scores', methods=['GET'])
def get_scores():
    return jsonify(load_scores())

# REST API to update a score
@app.route('/api/update', methods=['POST'])
def update_score_api():
    data = request.json
    person = data.get('person')
    change = data.get('change')
    scores = load_scores()
    if person in scores:
        scores[person] += change
        save_scores(scores)
    return jsonify(scores)

# Web route to serve the frontend
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Respect Score</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: white;
            font-size: 3.5rem;
            margin-bottom: 50px;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
            font-weight: bold;
            letter-spacing: 3px;
        }
        .cards-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            justify-items: center;
        }
        .person-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            width: 100%;
            max-width: 350px;
        }
        .person-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }
        .person-name {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .person-image {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin: 0 auto 30px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4rem;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            border: 4px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        .person-image:hover {
            transform: scale(1.05);
        }
        .score-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }
        .score-btn {
            width: 50px;
            height: 50px;
            border: none;
            border-radius: 50%;
            font-size: 1.5rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }
        .score-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        .minus-btn {
            background: linear-gradient(45deg, #ff4757, #ff3742);
            box-shadow: 0 4px 15px rgba(255, 71, 87, 0.4);
        }
        .minus-btn:hover:not(:disabled) {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(255, 71, 87, 0.6);
        }
        .plus-btn {
            background: linear-gradient(45deg, #2ed573, #1dd1a1);
            box-shadow: 0 4px 15px rgba(46, 213, 115, 0.4);
        }
        .plus-btn:hover:not(:disabled) {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(46, 213, 115, 0.6);
        }
        .score-display {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 10px 20px;
            min-width: 80px;
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .score-display.updating {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(1.1);
        }
        .status-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            transition: all 0.3s ease;
            z-index: 1000;
        }
        .status-online {
            background: linear-gradient(45deg, #2ed573, #1dd1a1);
            box-shadow: 0 4px 15px rgba(46, 213, 115, 0.4);
        }
        .status-updating {
            background: linear-gradient(45deg, #ffa502, #ff6348);
            box-shadow: 0 4px 15px rgba(255, 165, 2, 0.4);
        }
        .status-error {
            background: linear-gradient(45deg, #ff4757, #ff3742);
            box-shadow: 0 4px 15px rgba(255, 71, 87, 0.4);
        }
        @media (max-width: 768px) {
            h1 {
                font-size: 2.5rem;
                margin-bottom: 30px;
            }
            .person-card {
                padding: 20px;
            }
            .person-image {
                width: 120px;
                height: 120px;
                font-size: 3rem;
            }
            .status-indicator {
                top: 10px;
                right: 10px;
                padding: 8px 15px;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="status-indicator status-online" id="status">● Online</div>
    
    <div class="main-container">
        <h1>RESPECT SCORE</h1>
        <div class="cards-container">
            <div class="person-card">
                <div class="person-name">Ali</div>
                <div class="person-image">👤</div>
                <div class="score-container">
                    <button class="score-btn minus-btn" onclick="updateScore('ali', -1)">-1</button>
                    <div class="score-display" id="ali-score">0</div>
                    <button class="score-btn plus-btn" onclick="updateScore('ali', 1)">+1</button>
                </div>
            </div>
            <div class="person-card">
                <div class="person-name">Hamza</div>
                <div class="person-image">👤</div>
                <div class="score-container">
                    <button class="score-btn minus-btn" onclick="updateScore('hamza', -1)">-1</button>
                    <div class="score-display" id="hamza-score">0</div>
                    <button class="score-btn plus-btn" onclick="updateScore('hamza', 1)">+1</button>
                </div>
            </div>
            <div class="person-card">
                <div class="person-name">Yasir</div>
                <div class="person-image">👤</div>
                <div class="score-container">
                    <button class="score-btn minus-btn" onclick="updateScore('yasir', -1)">-1</button>
                    <div class="score-display" id="yasir-score">0</div>
                    <button class="score-btn plus-btn" onclick="updateScore('yasir', 1)">+1</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let scores = {};
        let isUpdating = false;

        // Status indicator elements
        const statusEl = document.getElementById('status');

        // Set status
        function setStatus(type, message) {
            statusEl.className = `status-indicator status-${type}`;
            statusEl.textContent = message;
        }

        // Load initial scores
        async function loadScores() {
            try {
                const response = await fetch('/api/scores');
                if (response.ok) {
                    scores = await response.json();
                    updateScoreDisplays();
                    setStatus('online', '● Online');
                } else {
                    throw new Error('Failed to load scores');
                }
            } catch (error) {
                console.error('Error loading scores:', error);
                setStatus('error', '● Error');
            }
        }

        // Update score displays
        function updateScoreDisplays() {
            for (const person in scores) {
                const el = document.getElementById(`${person}-score`);
                if (el) {
                    el.textContent = scores[person];
                    // Add animation
                    el.classList.add('updating');
                    setTimeout(() => el.classList.remove('updating'), 300);
                }
            }
        }

        // Update score function
        async function updateScore(person, change) {
            if (isUpdating) return; // Prevent multiple simultaneous updates
            
            isUpdating = true;
            setStatus('updating', '● Updating...');
            
            // Disable all buttons
            const buttons = document.querySelectorAll('.score-btn');
            buttons.forEach(btn => btn.disabled = true);

            try {
                const response = await fetch('/api/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ person, change })
                });

                if (response.ok) {
                    scores = await response.json();
                    updateScoreDisplays();
                    setStatus('online', '● Online');
                } else {
                    throw new Error('Failed to update score');
                }
            } catch (error) {
                console.error('Error updating score:', error);
                setStatus('error', '● Error');
                // Reload scores to sync with server
                setTimeout(loadScores, 1000);
            } finally {
                isUpdating = false;
                // Re-enable all buttons
                buttons.forEach(btn => btn.disabled = false);
            }
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(event) {
            if (isUpdating) return; // Don't allow keyboard shortcuts while updating
            
            switch(event.key) {
                case '1': updateScore('ali', 1); break;
                case '!': updateScore('ali', -1); break;
                case '2': updateScore('hamza', 1); break;
                case '@': updateScore('hamza', -1); break;
                case '3': updateScore('yasir', 1); break;
                case '#': updateScore('yasir', -1); break;
            }
        });

        // Auto-refresh scores every 5 seconds to keep in sync
        setInterval(loadScores, 5000);

        // Load scores when page loads
        window.addEventListener('load', loadScores);
    </script>
</body>
</html>"""

if __name__ == '__main__':
    print("🚀 Starting Respect Score Website (No WebSocket)...")
    print("📍 Open your browser and go to: http://127.0.0.1:8080")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    app.run(host='127.0.0.1', port=8080, debug=True)

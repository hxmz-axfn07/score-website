from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse
import threading
import time

class RespectScoreHandler(BaseHTTPRequestHandler):
    # JSON file to store scores
    SCORES_FILE = 'scores.json'
    scores_lock = threading.Lock()
    
    @classmethod
    def load_scores(cls):
        """Load scores from JSON file"""
        try:
            if os.path.exists(cls.SCORES_FILE):
                with open(cls.SCORES_FILE, 'r', encoding='utf-8') as f:
                    scores = json.load(f)
                    # Ensure all required people are in the scores
                    default_scores = {'ali': 0, 'hamza': 0, 'yasir': 0}
                    for person in default_scores:
                        if person not in scores:
                            scores[person] = default_scores[person]
                    return scores
            else:
                # Create default scores file if it doesn't exist
                default_scores = {'ali': 0, 'hamza': 0, 'yasir': 0}
                cls.save_scores(default_scores)
                return default_scores
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading scores: {e}")
            # Return default scores if file is corrupted
            default_scores = {'ali': 0, 'hamza': 0, 'yasir': 0}
            cls.save_scores(default_scores)
            return default_scores
    
    @classmethod
    def save_scores(cls, scores):
        """Save scores to JSON file"""
        try:
            with open(cls.SCORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(scores, f, indent=2, ensure_ascii=False)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scores saved to {cls.SCORES_FILE}")
        except IOError as e:
            print(f"Error saving scores: {e}")
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the main HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'index.html not found')
                
        elif parsed_path.path == '/api/scores':
            # Return current scores as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with self.scores_lock:
                scores = self.load_scores()
                self.wfile.write(json.dumps(scores, ensure_ascii=False).encode('utf-8'))
                
        else:
            # 404 for other paths
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/update':
            # Handle score updates
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                person = data.get('person')
                change = data.get('change')
                
                with self.scores_lock:
                    scores = self.load_scores()
                    
                    if person in scores and isinstance(change, int):
                        old_score = scores[person]
                        scores[person] += change
                        self.save_scores(scores)
                        
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {person.title()}: {old_score} → {scores[person]} ({change:+d})")
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        self.wfile.write(json.dumps(scores, ensure_ascii=False).encode('utf-8'))
                    else:
                        self.send_response(400)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(b'Invalid request: person not found or invalid change value')
                        
            except (json.JSONDecodeError, ValueError) as e:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Invalid JSON: {str(e)}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging with timestamp
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def get_local_ip():
    """Get local IP address for network access"""
    import socket
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RespectScoreHandler)
    
    # Initialize scores file
    print("📁 Initializing scores database...")
    initial_scores = RespectScoreHandler.load_scores()
    print(f"📊 Current scores: {initial_scores}")
    
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🏆 RESPECT SCORE SERVER")
    print("="*60)
    print(f"🚀 Server Status: RUNNING")
    print(f"📍 Local Access: http://localhost:{port}")
    print(f"🌐 Network Access: http://{local_ip}:{port}")
    print(f"💾 Data File: {RespectScoreHandler.SCORES_FILE}")
    print(f"📂 Working Directory: {os.getcwd()}")
    print("="*60)
    print("⌨️  Keyboard Shortcuts (on webpage):")
    print("   1/! = Ali +1/-1    2/@ = Hamza +1/-1    3/# = Yasir +1/-1")
    print("="*60)
    print("⏹️  Press Ctrl+C to stop the server")
    print("-"*60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        print("💾 All data has been saved to scores.json")
        httpd.server_close()

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8000.")
    
    # Check if HTML file exists
    if not os.path.exists('index.html'):
        print("❌ Error: index.html file not found!")
        print("Please make sure the HTML file is in the same directory as this script.")
        print(f"Current directory: {os.getcwd()}")
        sys.exit(1)
    
    run_server(port)


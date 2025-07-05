from flask import Flask, render_template
import subprocess
import os
import sys

# Set up Flask — assuming index.html is in the same directory as app.py
app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Get current directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Try to use venv Python, fallback to system Python if not found
    venv_python = os.path.join(base_dir, '../.venv/bin/python')
    if not os.path.exists(venv_python):
        print("⚠️ Virtual environment not found. Falling back to system Python.")
        venv_python = sys.executable  # fallback to current interpreter

    # Full path to game.py
    game_script = os.path.join(base_dir, 'game.py')

    # Start game.py with correct working directory
    try:
        subprocess.Popen([venv_python, game_script], cwd=base_dir)
        print("✅ game.py launched successfully.")
    except Exception as e:
        print(f"❌ Failed to launch game.py: {e}")

    # Start the Flask web server
    app.run(debug=True)






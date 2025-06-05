from flask import Flask, request, jsonify
import subprocess
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Automation System - Läuft!"

@app.route('/create-video', methods=['POST'])
def create_video():
    data = request.json
    topic = data.get('topic', 'Wissenschaft')
    
    # Starte den Automationsprozess im Hintergrund
    thread = threading.Thread(target=run_automation, args=(topic,))
    thread.start()
    
    return jsonify({"status": "started", "topic": topic})

def run_automation(topic):
    # Hier wird der eigentliche Automationsprozess gestartet
    subprocess.run([
        'python', 'automation.py',
        '--topic', topic,
        '--output', 'output.mp4'
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

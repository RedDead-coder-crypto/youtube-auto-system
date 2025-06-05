import argparse
import openai
from elevenlabs import generate, save
import requests
import os
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# Argumente parsen
parser = argparse.ArgumentParser()
parser.add_argument('--topic', default='Wissenschaft')
parser.add_argument('--output', default='output.mp4')
args = parser.parse_args()

# API Keys aus Umgebungsvariablen
openai.api_key = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

# 1. Skript generieren
def generate_script(topic):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Erstelle ein YouTube-Skript mit 3 Fakten über {topic}. Maximal 100 Wörter."
        }]
    )
    return response.choices[0].message['content']

# 2. Voiceover erstellen
def create_voiceover(text):
    audio = generate(
        text=text,
        voice="Bella",
        model="eleven_monolingual_v2",
        api_key=ELEVENLABS_API_KEY
    )
    save(audio, "voiceover.mp3")
    return "voiceover.mp3"

# 3. Bilder herunterladen
def download_images(topic, count=3):
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(
        f"https://api.pexels.com/v1/search?query={topic}&per_page={count}",
        headers=headers
    )
    photos = response.json().get('photos', [])
    
    image_paths = []
    for i, photo in enumerate(photos[:count]):
        img_url = photo['src']['large']
        img_data = requests.get(img_url).content
        path = f"image_{i}.jpg"
        with open(path, "wb") as f:
            f.write(img_data)
        image_paths.append(path)
    
    return image_paths

# 4. Video erstellen
def create_video(voiceover_path, image_paths):
    audio = AudioFileClip(voiceover_path)
    duration = audio.duration
    segment_duration = duration / len(image_paths)
    
    clips = []
    for image_path in image_paths:
        clip = ImageClip(image_path).set_duration(segment_duration)
        clips.append(clip)
    
    video = concatenate_videoclips(clips)
    video = video.set_audio(audio)
    video.write_videofile(args.output, fps=24)
    
    return args.output

if __name__ == "__main__":
    print("Starte Automatisierung...")
    script = generate_script(args.topic)
    print(f"Skript generiert: {script[:50]}...")
    
    voiceover = create_voiceover(script)
    print("Voiceover erstellt")
    
    images = download_images(args.topic)
    print(f"{len(images)} Bilder heruntergeladen")
    
    video_path = create_video(voiceover, images)
    print(f"Video erstellt: {video_path}")

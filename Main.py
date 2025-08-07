import os
import openai
import subprocess
from glob import glob

openai.api_key = os.getenv("OPENAI_API_KEY")
TWITCH_VOD_URL = "https://www.twitch.tv/videos/2527829496"
OUTPUT_DIR = "clips"
CLIP_LENGTH = 300  # Sekunden

def download_vod(url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    subprocess.run(["yt-dlp", url, "-o", "vod.mp4"], check=True)

def split_video():
    subprocess.run([
        "ffmpeg", "-i", "vod.mp4", "-c", "copy",
        "-map", "0", "-segment_time", str(CLIP_LENGTH),
        "-f", "segment", f"{OUTPUT_DIR}/part_%03d.mp4"
    ], check=True)

def analyse_clips():
    for clip in sorted(glob(f"{OUTPUT_DIR}/part_*.mp4")):
        print(f"🧠 Analysiere {clip}")
        text = transcribe_with_gpt(clip)
        if is_clip_viral(text):
            save_caption(clip, text)

def transcribe_with_gpt(clip_path):
    with open(clip_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
    return transcript["text"]

def is_clip_viral(text):
    prompt = f"""
Hier ist ein Twitch-Ausschnitt:
{text}
Ist das witzig, spannend oder viral? Antworte nur mit JA oder NEIN.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return "JA" in response.choices[0].message.content.upper()

def save_caption(clip_path, transcript):
    caption_prompt = f"Erstelle eine virale Instagram Caption für:\n{transcript}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": caption_prompt}]
    )
    caption = response.choices[0].message.content.strip()
    with open(clip_path.replace(".mp4", ".txt"), "w") as f:
        f.write(caption)

if __name__ == "__main__":
    download_vod(TWITCH_VOD_URL)
    split_video()
    analyse_clips()

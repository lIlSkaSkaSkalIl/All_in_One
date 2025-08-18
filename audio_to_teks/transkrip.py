# @title 🧠 Transcribe Audio
# @markdown - This cell will convert audio to text using Whisper.

import subprocess
import sys
import shutil
import os
import time
import json

# ✅ Unified Logger
def log(message: str, level: str = "INFO"):
    print(f"[{level}] {message}")

# Install ffmpeg if missing
if not shutil.which("ffmpeg"):
    log("ffmpeg not found. Installing via apt...")
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", "ffmpeg"])

# Install whisper if not already installed
try:
    import whisper
except ImportError:
    log("Installing whisper...")
    subprocess.run([sys.executable, "-m", "pip", "install", "git+https://github.com/openai/whisper.git", "-q"])
    import whisper
    log("whisper installed successfully.")

# 📌 Input Parameters
model_name = "base"  # @param ["tiny", "base", "small", "medium", "large"]
audio_path = "/content/media_toolkit/Customizing GNOME Desktop | Gnome Customization Guide.m4a"  # @param {type:"string"}
output_path = "/content/media_toolkit/transkip_audio"  # @param {type:"string"}

# ✅ Show short preview of the transcript
def show_text_preview(text: str, max_chars: int = 100):
    preview = text.strip()[:max_chars].replace("\n", " ") + "..."
    print(f"[PREVIEW] {preview}")

# ✅ Transcription function
def transcribe_audio(audio_path: str, model_name: str = "base", output_path: str = "") -> str:
    """
    Transcribe audio using OpenAI Whisper and save segments to JSON.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"[ERROR] File not found: {audio_path}")

    if not output_path.strip():
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = os.path.join("/content/media_toolkit/transcripts", base_name)

    os.makedirs(output_path, exist_ok=True)

    log(f"Loading Whisper model: {model_name}", "INFO")
    start_time = time.time()
    model = whisper.load_model(model_name)

    log("Starting transcription...", "INFO")
    result = model.transcribe(audio_path, verbose=True)
    end_time = time.time()
    log(f"Transcription completed in {end_time - start_time:.2f} seconds", "SUCCESS")

    # Save segments to JSON
    json_output_path = os.path.join(output_path, "segments.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(result["segments"], f, ensure_ascii=False, indent=2)

    log(f"Transcription saved to: {json_output_path}", "SUCCESS")
    show_text_preview(result["text"])

    return json_output_path

# ✅ Run transcription
transcribe_audio(audio_path, model_name, output_path)

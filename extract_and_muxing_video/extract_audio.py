# @title 🎧 Extract Audio from Video
import os
import subprocess
import shutil
import sys


# ✅ Unified Logging
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# Check if ffmpeg is available, install if not (for Colab or Linux)
if not shutil.which("ffmpeg"):
    log("ffmpeg not found. Installing via apt...")
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", "ffmpeg"])
    if not shutil.which("ffmpeg"):
        log("ffmpeg installation failed.", "ERROR")
        sys.exit()
    else:
        log("ffmpeg installed successfully.")


# 🔄 Extract audio from a single video
def extract_audio(video_path, output_path, output_name="", index=None, total=None):
    if not os.path.exists(video_path):
        log(f"File not found: {video_path}", "ERROR")
        return

    os.makedirs(output_path, exist_ok=True)

    # Progress indicator
    progress = f"[{index+1}/{total}]" if index is not None and total is not None else ""

    # Output file name
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_name = output_name.strip() if output_name.strip() else base_name
    audio_path = os.path.join(output_path, f"{audio_name}.m4a")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",  # no video
        "-acodec",
        "aac",  # encode audio to AAC
        audio_path,
    ]

    log(f"{progress} Input Video: {video_path}")
    log(f"{progress} Output Audio: {audio_path}")
    log(f"{progress} Running ffmpeg...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        log(f"{progress} Audio extracted successfully.", "SUCCESS")
    else:
        log(f"{progress} Failed to extract audio", "ERROR")
        print(result.stderr)


# 📁 Batch process all video files in a folder
def process_folder(folder_path, output_path):
    video_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
        and f.lower().endswith((".mp4", ".mkv", ".webm", ".mov"))
    ]

    log(f"Folder mode: processing {len(video_files)} video files in: {folder_path}")

    for idx, fpath in enumerate(sorted(video_files)):
        extract_audio(fpath, output_path, index=idx, total=len(video_files))

    log("All files in the folder have been processed.", "SUCCESS")


# 📌 Input Form (Colab)
video_input_path = ""  # @param {type:"string"}
output_path = "/content/media_toolkit/audio"  # @param {type:"string"}
output_name = ""  # @param {type:"string"}

# 🚀 Execution
if os.path.isdir(video_input_path):
    process_folder(video_input_path, output_path)
elif os.path.isfile(video_input_path):
    extract_audio(video_input_path, output_path, output_name)
else:
    log("Input path not found!", "ERROR")

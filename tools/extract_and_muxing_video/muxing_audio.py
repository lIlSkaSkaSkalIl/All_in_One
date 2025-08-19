# @title 🔄 Muxing Audio to Video
import subprocess
import shutil
import os
import sys


# ✅ Unified Logging
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# Check if ffmpeg is installed, install if not (for Colab or Linux)
if not shutil.which("ffmpeg"):
    log("ffmpeg not found. Installing via apt...")
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", "ffmpeg"])
    if not shutil.which("ffmpeg"):
        log("ffmpeg installation failed.", "ERROR")
        sys.exit()
    else:
        log("ffmpeg installed successfully.")


# 🔀 Get & sort files by extension
def get_sorted_files(path, extensions):
    if os.path.isfile(path):
        if path.lower().endswith(extensions):
            return [path]
        return []
    return sorted(
        [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.lower().endswith(extensions)
        ]
    )


# 🔧 Mux one video/audio pair
def mux_pair(video_path, audio_path, output_path, index, total):
    base_name = os.path.basename(video_path)  # Keep the original video filename
    output_file = os.path.join(output_path, base_name)

    progress = f"[{index+1}/{total}]"
    log(f"{progress} Video : {os.path.basename(video_path)}", "VIDEO")
    log(f"{progress} Audio : {os.path.basename(audio_path)}", "AUDIO")
    log(f"{progress} Output: {output_file}", "OUTPUT")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        output_file,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"{progress} Successfully muxed.", "SUCCESS")
    else:
        log(f"{progress} Failed to mux.", "ERROR")
        print(result.stderr)


# 🚀 Batch muxing process
def batch_mux(video_input, audio_input, output_folder):
    log("Starting batch muxing based on sorted order...", "PROCESS")

    # Handle both file and folder inputs
    video_files = get_sorted_files(video_input, (".mp4", ".mkv", ".webm", ".mov"))
    audio_files = get_sorted_files(audio_input, (".m4a", ".aac", ".mp3", ".wav"))

    log(f"Total videos: {len(video_files)}", "COUNT")
    log(f"Total audios: {len(audio_files)}", "COUNT")

    if not video_files:
        log("No video files found!", "ERROR")
        return
    if not audio_files:
        log("No audio files found!", "ERROR")
        return

    if len(video_files) != len(audio_files):
        log(
            "Number of videos and audios do NOT match. Will process only the smallest count.",
            "WARNING",
        )

    total = min(len(video_files), len(audio_files))
    os.makedirs(output_folder, exist_ok=True)

    for i in range(total):
        mux_pair(video_files[i], audio_files[i], output_folder, i, total)

    log("Finished processing all file pairs.", "DONE")


# 📌 Input Paths (for Colab or script use)
video_input = ""  # @param {type:"string"}
audio_input = ""  # @param {type:"string"}
output_folder = "/content/media_toolkit"  # @param {type:"string"}

# 🚀 Run muxing
batch_mux(video_input, audio_input, output_folder)

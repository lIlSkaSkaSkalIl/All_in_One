# @title 🧠 Extract Video Metadata to JSON

import subprocess
import json
import os
import shutil


def log(message, level="INFO"):
    print(f"[{level}] {message}")


# 📥 User input
video_path = ""  # @param {type:"string"}
output_folder = "/content/media_toolkit/metadata"  # @param {type:"string"}


# ✅ Check if ffmpeg is installed
def check_dependency():
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        log("ffmpeg not found. Installing ffmpeg...")
        os.system("apt-get update -y && apt-get install -y ffmpeg")
        log("ffmpeg installed successfully.")
    else:
        log("ffmpeg and ffprobe are available.")


def extract_metadata_to_json(video_path: str, output_folder: str = "metadata"):
    # 🔍 Validate video file
    if not os.path.exists(video_path):
        log(f"File not found: {video_path}", level="ERROR")
        return

    # 🗂️ Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        log(f"Output folder not found. Creating: {output_folder}")
        os.makedirs(output_folder, exist_ok=True)

    log(f"Starting metadata extraction for: {video_path}")

    # 📄 Create JSON file name based on video name
    video_filename = os.path.basename(video_path)
    json_filename = os.path.splitext(video_filename)[0] + ".json"
    output_json_path = os.path.join(output_folder, json_filename)

    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]

    try:
        log("Running ffprobe...")
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode != 0:
            log("Failed to run ffprobe.", level="ERROR")
            log(result.stderr.strip(), level="WARNING")
            return

        metadata = json.loads(result.stdout)
        log("Metadata successfully extracted.", level="INFO")

        with open(output_json_path, "w") as f:
            json.dump(metadata, f, indent=2)
        log(f"Metadata saved to: {output_json_path}\n")

        return metadata

    except Exception as e:
        log(f"An error occurred: {e}", level="ERROR")


# run check dependency
check_dependency()

# 🚀 Run the function
extract_metadata_to_json(video_path, output_folder)

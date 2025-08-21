# @title 🎬 Extract All Soft Subtitles from Video (File or Folder)
import subprocess
import shutil
import os
import json
import sys
from typing import List, Union


# ✅ Unified Logging
def log(message: str, level: str = "INFO"):
    print(f"[{level}] {message}")


# ✅ Check and install ffmpeg if not found (for Colab or Linux)
if not shutil.which("ffmpeg"):
    log("ffmpeg not found. Installing via apt...")
    subprocess.run(
        ["apt-get", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    subprocess.run(
        ["apt-get", "install", "-y", "ffmpeg"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not shutil.which("ffmpeg"):
        log("ffmpeg installation failed.", "ERROR")
        sys.exit(1)
    else:
        log("ffmpeg installed successfully.")

# 📌 Input (for Colab use)
input_path = ""  # @param {type:"string"}
output_dir = ""  # @param {type:"string"}


# 🎯 Get subtitle track information using ffprobe
def get_subtitle_tracks(video_path: str) -> List[dict]:
    """Return all subtitle tracks from the video file"""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "s",
        "-show_entries",
        "stream=index:stream_tags=language",
        "-of",
        "json",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return data.get("streams", [])
    except subprocess.CalledProcessError as e:
        log(f"Error probing {video_path}: {e.stderr}", "ERROR")
        return []
    except json.JSONDecodeError:
        log(f"Invalid JSON output from ffprobe for {video_path}", "ERROR")
        return []


# 🛠️ Build output subtitle file path (auto rename + avoid overwrite)
def build_output_path(
    video_path: str, lang: Union[str, None], index: int, output_dir: str = ""
) -> str:
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    suffix = lang if lang else str(index + 1)
    target_dir = output_dir if output_dir else os.path.dirname(video_path)
    os.makedirs(target_dir, exist_ok=True)

    # Initial target file
    file_path = os.path.join(target_dir, f"{base_name}.{suffix}.srt")

    # Avoid overwrite by appending index if file exists
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(target_dir, f"{base_name}.{suffix}({counter}).srt")
        counter += 1

    return file_path


# 🔄 Extract all subtitle tracks to individual .srt files
def extract_subtitles_from_file(video_path: str, output_dir: str = "") -> bool:
    """Extract all subtitle tracks from a single video file. Returns True if successful."""
    if not os.path.isfile(video_path):
        log(f"File not found: {video_path}", "ERROR")
        return False

    tracks = get_subtitle_tracks(video_path)
    if not tracks:
        log(f"No subtitle tracks found in {video_path}", "WARNING")
        return False

    log(f"Found {len(tracks)} subtitle track(s) in {os.path.basename(video_path)}")

    success = False
    for i, track in enumerate(tracks):
        lang = track.get("tags", {}).get("language")
        output_file = build_output_path(video_path, lang, i, output_dir)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-map",
            f"0:s:{i}",
            "-c:s",
            "srt",
            output_file,
        ]
        log(f"Extracting track {i} ({lang if lang else 'unknown'})...")
        try:
            subprocess.run(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
            log(f"Saved: {output_file}", "SUCCESS")
            success = True
        except subprocess.CalledProcessError as e:
            log(f"Failed to extract track {i} from {video_path}: {e}", "ERROR")

    return success


# 📂 Process all video files in a directory
def extract_subtitles_from_folder(folder_path: str, output_dir: str = "") -> int:
    """Extract subtitles from all video files in folder. Returns count of processed files."""
    if not os.path.isdir(folder_path):
        log(f"Folder not found: {folder_path}", "ERROR")
        return 0

    video_extensions = (".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv")
    processed_files = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(video_extensions):
                video_path = os.path.join(root, file)
                log(f"Processing: {video_path}")
                if extract_subtitles_from_file(video_path, output_dir):
                    processed_files += 1

    return processed_files


# 🚀 Main execution function
def main(input_path: str, output_dir: str):
    if os.path.isfile(input_path):
        log(f"Processing single file: {input_path}")
        extract_subtitles_from_file(input_path, output_dir)
    elif os.path.isdir(input_path):
        log(f"Processing folder: {input_path}")
        count = extract_subtitles_from_folder(input_path, output_dir)
        log(f"Finished! Processed {count} video files.", "SUCCESS")
    else:
        log(f"Path not found: {input_path}", "ERROR")
        sys.exit(1)


# ▶️ Execute the extraction
if __name__ == "__main__":
    main(input_path.strip(), output_dir.strip())

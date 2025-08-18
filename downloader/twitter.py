# ===============================> Cell 1 <==================================== #

# @title [Manual] Upload Cookies
# @markdown - Upload cookies.txt file (for Twitter download auth)

from google.colab import files
import os


def log(message, level="INFO"):
    print(f"[{level}] {message}")


def process_uploaded_cookies(file_dict: dict, target_name="cookies.txt") -> str | None:
    cookies_file = None

    # Find .txt file
    for filename in file_dict.keys():
        if filename.endswith(".txt"):
            cookies_file = filename
            break

    if cookies_file and os.path.exists(cookies_file):
        if cookies_file != target_name:
            os.rename(cookies_file, target_name)
            log(f"Renamed '{cookies_file}' to '{target_name}'")
        else:
            log("Cookies file is already named 'cookies.txt'")

        print("[PREVIEW] First 3 lines of cookies.txt:")
        try:
            with open(target_name, "r", encoding="utf-8") as f:
                for _ in range(3):
                    line = f.readline()
                    if line:
                        print("   ", line.strip())
        except UnicodeDecodeError:
            log("Failed to display cookies preview (unsupported encoding)", "ERROR")

        return os.path.abspath(target_name)
    else:
        log("No valid .txt cookies file found or upload failed", "ERROR")
        return None


log("Please upload your cookies.txt file (for Twitter download auth)")
uploaded_files = files.upload()

cookies_path = process_uploaded_cookies(uploaded_files)

# ===============================> Cell 2 <==================================== #

# @title 🎞️ Download Twitter Video
# @markdown - Input tweet URL (single/multiple videos)
tweet_url = ""  # @param {type: "string"}
video_dir = ""  # @param {type: "string"}

import os
import re
import json
import subprocess
import time
import shutil
from tqdm import tqdm


def log(message, level="INFO"):
    print(f"[{level}] {message}")


def install_dependencies():
    """Install required dependencies if not already installed"""
    required = ["yt-dlp"]
    to_install = []

    for dep in required:
        if not shutil.which(dep):
            to_install.append(dep)

    if to_install:
        print("[INFO] Installing missing dependencies...")
        subprocess.run(["pip", "install", "yt-dlp"], stdout=subprocess.DEVNULL)
        print("[INFO] Dependencies installed successfully")


def format_duration(seconds: float | int | str) -> str:
    """Convert duration in seconds to hh:mm:ss format."""
    try:
        seconds = float(seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"
    except:
        return "?"


def download_tweet_video(
    tweet_url: str, video_dir: str, cookies_path: str = "cookies.txt"
):
    # 🆔 Extract Tweet ID - Biarkan print asli
    match = re.search(r"/status/(\d+)", tweet_url)
    if not match:
        log("Invalid URL: Tweet ID not found.", "ERROR")
        raise ValueError("Invalid tweet URL")
    tweet_id = match.group(1)

    # 📁 Prepare directories - Tetap gunakan print
    os.makedirs(video_dir, exist_ok=True)
    metadata_dir = os.path.join(video_dir, "metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    # 🍪 Check for cookies - Tetap gunakan print
    use_cookies = os.path.exists(cookies_path)
    cookie_args = ["--cookies", cookies_path] if use_cookies else []

    # 📥 Download video - Progress bar tetap pakai tqdm
    log("Starting tweet video download...")
    start_time = time.time()
    output_template = os.path.join(video_dir, "%(id)s.%(ext)s")

    command = (
        [
            "yt-dlp",
            "-f",
            "best",
            "--write-info-json",
            "-o",
            output_template,
        ]
        + cookie_args
        + [tweet_url]
    )

    # ▶️ Progress bar tetap sama
    progress_bar = tqdm(total=100, desc="📥 Download", unit="%")
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    for line in process.stdout:
        line = line.strip()
        if "%" in line:
            match = re.search(r"(\d{1,3}\.\d)%", line)
            if match:
                percent = float(match.group(1))
                progress_bar.n = int(percent)
                progress_bar.refresh()
        elif "[download]" in line or "Destination" in line:
            print(line)
    process.wait()
    progress_bar.n = 100
    progress_bar.refresh()
    progress_bar.close()

    end_time = time.time()
    elapsed = round(end_time - start_time, 2)
    log("Download completed.")

    video_exts = (".mp4", ".mkv", ".webm", ".mov", ".avi")
    downloaded_files = [
        os.path.join(video_dir, f)
        for f in os.listdir(video_dir)
        if f.lower().endswith(video_exts)
    ]

    for video_file in downloaded_files:
        video_id = os.path.splitext(os.path.basename(video_file))[0]
        info_file = os.path.join(video_dir, f"{video_id}.info.json")
        if os.path.exists(info_file):
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta_save_path = os.path.join(
                    metadata_dir, f"tweet_meta_{video_id}.json"
                )
                with open(meta_save_path, "w", encoding="utf-8") as out:
                    json.dump(meta, out, ensure_ascii=False, indent=2)
                os.remove(info_file)
                log(f"Metadata saved to: {meta_save_path}")
            except Exception as e:
                log(f"Failed to process metadata: {e}", "ERROR")
        else:
            log(f"Metadata not found for {video_file}", "ERROR")

    # 📊 Summary - Tetap gunakan print asli
    print("\n📊 Download Summary:")
    print(f"├─📌 Tweet URL        : {tweet_url}")
    print(f"├─🆔 Tweet ID         : {tweet_id}")
    print(f"├─🔐 Cookies Used     : {'Yes' if use_cookies else 'No'}")
    print(f"├─⏱️ Saved Time       : {elapsed:.2f} sec")
    print(f"├─📹 Videos Downloaded: {len(downloaded_files)} file(s)")
    print(f"├─📂 Metadata Folder  : {metadata_dir}")
    print(f"└─📜 File List        :")

    for i, f in enumerate(downloaded_files, 1):
        fname = os.path.basename(f)
        print(f"   {i}. {fname}")
        video_id = os.path.splitext(fname)[0]
        meta_path = os.path.join(metadata_dir, f"tweet_meta_{video_id}.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as meta_file:
                    meta = json.load(meta_file)
                width = meta.get("width") or "?"
                height = meta.get("height") or "?"
                resolution = f"{width}x{height}" if width and height else "?"
                size_mb = os.path.getsize(f) / (1024 * 1024)
                duration = meta.get("duration") or "?"
                formated_duration = format_duration(duration)
                print(f"      ├─🎞️ Resolution : {resolution}")
                print(f"      ├─💾 File Size  : {size_mb:.2f} MB")
                print(f"      └─⏱️ Duration   : {formated_duration}")
            except Exception as e:
                print(f"      └─⚠️ Failed to read metadata: {e}")
        else:
            print(f"      └─⚠️ Metadata not found.")


install_dependencies()
download_tweet_video(tweet_url, video_dir)

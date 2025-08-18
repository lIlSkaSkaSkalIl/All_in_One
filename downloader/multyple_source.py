# ===============================> Cell 1 <==================================== #

# @title ⚙️ Save Download Configuration as JSON
download_type = "m3u8"  # @param ["auto", "google_drive", "direct", "m3u8"]
video_ext = "mp4"  # @param ["mp4", "mkv", "webm", "flv", "avi"]
video_url = ""  # @param {type:"string"}
file_name = ""  # @param {type:"string"}
video_dir = "/content/media_toolkit/sub"  # @param {type:"string"}
config_path = (
    "/content/media_toolkit/config/video_config.json"  # @param {type:"string"}
)

import os
import json
from datetime import datetime


def log(message, level="INFO"):
    print(f"[{level}] {message}")


def print_download_info(
    video_url: str,
    download_type: str,
    output_path: str,
    file_name: str,
    config_path: str,
):
    log(f"Download Info Created Successfully")
    print(f"╭🎯 URL           : {video_url}")
    print(f"├🧩 Download Type : {download_type}")
    print(f"├📁 Filename      : {file_name}")
    print(f"├📁 Saving to     : {output_path}")
    print(f"╰💾 Json saved to : {config_path}")


def save_config_to_json(
    download_type: str,
    video_url: str,
    file_name: str,
    video_ext: str,
    video_dir: str,
    config_path: str,
):
    # Buat folder video
    os.makedirs(video_dir, exist_ok=True)
    log("Video folder is ready.")

    # Buat folder tempat file config jika belum ada
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    log("Config folder is ready.")

    # Format nama file jika kosong/tidak valid
    if not file_name.strip():
        timestamp = datetime.now().strftime("video_%Y%m%d_%H%M%S")
        file_name = f"{timestamp}.{video_ext}"
        log("Filename was generated based on current time.")
    elif not file_name.endswith(f".{video_ext}"):
        file_name += f".{video_ext}"
        log(f"Added .{video_ext} extension to the filename.")

    output_path = os.path.join(video_dir, file_name)

    # Simpan konfigurasi ke file JSON
    config = {
        "download_type": download_type,
        "video_url": video_url,
        "file_name": file_name,
        "video_ext": video_ext,
        "video_dir": video_dir,
        "output_path": output_path,
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    print_download_info(video_url, download_type, output_path, file_name, config_path)

    return output_path, config_path


# ▶️ Call the function
output_path, config_path = save_config_to_json(
    download_type, video_url, file_name, video_ext, video_dir, config_path
)

# ===============================> Cell 2 <==================================== #

# @title 🔽 Load Config and Download Video
import os
import re
import json
import subprocess
import shutil
import time


def install_dependencies():
    """Install required dependencies if not already installed"""
    required = ["yt-dlp", "aria2", "ffmpeg"]
    to_install = []

    for dep in required:
        if not shutil.which(dep):
            to_install.append(dep)

    if to_install:
        print("[INFO] Installing missing dependencies...")
        subprocess.run(["apt-get", "update"], stdout=subprocess.DEVNULL)
        subprocess.run(
            ["apt-get", "install", "-y", "aria2", "ffmpeg"], stdout=subprocess.DEVNULL
        )
        subprocess.run(["pip", "install", "yt-dlp"], stdout=subprocess.DEVNULL)
        print("[INFO] Dependencies installed successfully")


def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] Config file not found: {path}")
    with open(path, "r") as f:
        config = json.load(f)
    return config


def log(message, level="INFO"):
    print(f"[{level}] {message}")


def is_m3u8(url: str) -> bool:
    return url.endswith(".m3u8") or ".m3u8?" in url


def is_drive(url: str) -> bool:
    return "drive.google.com" in url


def extract_drive_id(url: str) -> str | None:
    patterns = [
        r"drive\.google\.com/file/d/([^/]+)",
        r"drive\.google\.com/open\?id=([^&]+)",
        r"drive\.google\.com/uc\?id=([^&]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def command_exists(command):
    return shutil.which(command) is not None


def download_summary(path, elapsed):
    if os.path.exists(path):
        size = os.path.getsize(path) / (1024 * 1024)
        fname = os.path.basename(path)
        print(f"\n[SUCCESS] Download complete! File saved to: {path}")
        print(f"╭📄 Filename   : {fname}")
        print(f"├📦 File size  : {size:.2f} MB")
        print(f"╰⏱️ Saved Time : {elapsed:.2f} sec")
    else:
        log("Download finished, but file was not found.", "WARNING")


def get_format_with_ffprobe(video_path: str) -> str:
    cmd = [
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
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            return "unknown"
        metadata = json.loads(result.stdout)
        return metadata.get("format", {}).get("format_name", "unknown")
    except:
        return "unknown"


def print_config_summary(config: dict):
    print(f"[INFO] Download configuration:")
    print(f"╭🎯 URL           : {config.get('video_url')}")
    print(f"├🧩 Download Type : {config.get('download_type')}")
    print(f"├📄 File Name     : {config.get('file_name')}")
    print(f"├📁 Output Folder : {config.get('video_dir')}")
    print(f"├📦 Output Path   : {config.get('output_path')}")
    print(f"╰🎞️ Extension     : {config.get('video_ext')}\n")


def download_video_by_type(
    download_type: str,
    video_url: str,
    output_path: str,
    video_dir: str,
    video_ext: str = "mp4",
    config: dict = None,
):
    # Install dependencies first
    install_dependencies()

    def safe_run(cmd):
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in process.stdout:
            print(f"{line.strip()[:150]}", flush=True)
        process.wait()

    tool = download_type
    if tool == "auto":
        if is_drive(video_url):
            tool = "google_drive"
        elif is_m3u8(video_url):
            tool = "m3u8"
        else:
            tool = "direct"

    log(f"Using download tool: {tool}")

    start = time.time()

    temp_path = os.path.join(video_dir, "temp_dl")
    os.makedirs(temp_path, exist_ok=True)
    temp_output = os.path.join(temp_path, "downloaded_video")

    if tool == "google_drive":
        try:
            import gdown
        except ImportError:
            log("Installing gdown...", "INFO")
            subprocess.run(["pip", "install", "gdown"], stdout=subprocess.DEVNULL)
            import gdown

        log("Downloading from Google Drive...")
        if config:
            print_config_summary(config)
        drive_id = extract_drive_id(video_url)
        if not drive_id:
            raise ValueError("[ERROR] Unable to detect Google Drive ID.")
        temp_file = temp_output + ".mp4"
        gdown.download(
            f"https://drive.google.com/uc?id={drive_id}", temp_file, quiet=False
        )

    elif tool == "m3u8":
        log("Downloading from M3U8 using yt-dlp + aria2c...")
        if config:
            print_config_summary(config)
        cmd = [
            "yt-dlp",
            "--downloader",
            "aria2c",
            "--retries",
            "5",
            "--downloader-args",
            "aria2c:-x 16 -j 32 -s 32 -k 1M",
            "--merge-output-format",
            video_ext,
            "-o",
            temp_output + ".%(ext)s",
            video_url,
        ]
        safe_run(cmd)

    elif tool == "direct":
        log("Downloading from Direct Link using yt-dlp...")
        if config:
            print_config_summary(config)
        cmd = ["yt-dlp", "-o", temp_output + ".%(ext)s", "--retries", "3", video_url]
        safe_run(cmd)

    else:
        raise ValueError("[ERROR] Unknown download type!")

    downloaded_file_path = None
    for f in os.listdir(temp_path):
        if f.startswith("downloaded_video") and f.lower().endswith(
            (".mp4", ".mkv", ".webm", ".ts")
        ):
            downloaded_file_path = os.path.join(temp_path, f)
            break

    if not downloaded_file_path or not os.path.exists(downloaded_file_path):
        raise FileNotFoundError("[ERROR] No video file found after download.")

    detected_format = get_format_with_ffprobe(downloaded_file_path)
    log(f"Detected container format: {detected_format}")

    final_ext = os.path.splitext(downloaded_file_path)[1].lstrip(".").lower()
    if final_ext != video_ext.lower():
        log(f"Converting to .{video_ext} using ffmpeg (no re-encode)...")
        fixed_output = os.path.splitext(output_path)[0] + f".{video_ext}"
        convert_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            downloaded_file_path,
            "-c",
            "copy",
            fixed_output,
        ]
        safe_run(convert_cmd)
        shutil.move(fixed_output, output_path)
    else:
        shutil.move(downloaded_file_path, output_path)

    try:
        shutil.rmtree(temp_path)
    except Exception:
        pass

    end = time.time()
    download_summary(output_path, elapsed=end - start)


# ▶️ Run
config_path = (
    "/content/media_toolkit/config/video_config.json"  # @param {type:"string"}
)
config = load_config(config_path)

# Pastikan ekstensi output sesuai dengan keinginan user
if not config["output_path"].endswith(f".{config['video_ext']}"):
    config["output_path"] = (
        os.path.splitext(config["output_path"])[0] + f".{config['video_ext']}"
    )

download_video_by_type(
    config["download_type"],
    config["video_url"],
    config["output_path"],
    config["video_dir"],
    config.get("video_ext", "mp4"),
    config=config,
)

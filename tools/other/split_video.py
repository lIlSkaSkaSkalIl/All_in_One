# =======================> Cell 1 <==================== #

# @title 📋 Extract & Save Metadata
import os
import subprocess
import json
import sys


# 🔧 Custom Logging Function
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# @title 🔧 Dependency Installation
log("Checking and installing required dependencies...")

try:
    import ffmpeg

    log("ffmpeg-python is already installed")
except ImportError:
    log("Installing ffmpeg-python package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-python"])
    log("ffmpeg-python installed successfully", level="SUCCESS")

try:
    # Check if ffprobe is available
    subprocess.run(
        ["ffprobe", "-version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    log("ffprobe is already installed and available")
except (subprocess.CalledProcessError, FileNotFoundError):
    log("Installing ffmpeg (includes ffprobe)...", level="WARNING")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True)
        log("ffmpeg installed successfully", level="SUCCESS")
    except subprocess.CalledProcessError as e:
        log(f"Failed to install ffmpeg: {str(e)}", level="ERROR")
        sys.exit(1)

log("All dependencies are ready", level="SUCCESS")

# @title ⚙️ Main Script
# 🔧 Parameters
video_path = ""  # @param {type:"string"}
json_dir = "/content/media_toolkit/metadata"  # @param {type:"string"}

base_name = os.path.splitext(os.path.basename(video_path))[0]
json_path = os.path.join(json_dir, f"{base_name}.json")


def extract_metadata(video_path: str) -> dict:
    """Extract video metadata using ffprobe"""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            video_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return json.loads(result.stdout)


def save_metadata(metadata: dict, output_path: str):
    """Save metadata to JSON file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)


def summarize_metadata(metadata: dict):
    """Extract key metadata metrics"""
    duration = float(metadata["format"]["duration"])
    size_mb = float(metadata["format"]["size"]) / (1024 * 1024)
    bitrate_kbps = float(metadata["format"]["bit_rate"]) / 1000
    return duration, size_mb, bitrate_kbps


def show_metadata_summary(
    duration: float, size_mb: float, bitrate_kbps: float, path: str
):
    """Display formatted metadata summary (keeps original print with icons)"""
    filename = os.path.basename(path)
    print(f"╭📄 Filename   : {filename}")
    print(f"├🕒 Duration   : {duration:.2f} seconds")
    print(f"├💾 Size       : {size_mb:.2f} MB")
    print(f"├📶 Bitrate    : {bitrate_kbps:.0f} kbps")
    print(f"╰🎞 Video Path : {path}")


# 🔍 Process
if not os.path.exists(video_path):
    log("Video file does not exist", level="ERROR")
else:
    try:
        log("Extracting video metadata...")
        metadata = extract_metadata(video_path)
        metadata["input_video_path"] = video_path  # Inject path

        log(f"Saving metadata to: {json_path}")
        save_metadata(metadata, json_path)

        # Show summary (keeps original print format with icons)
        duration, size_mb, bitrate_kbps = summarize_metadata(metadata)
        show_metadata_summary(duration, size_mb, bitrate_kbps, video_path)
        log("Metadata extraction completed successfully", level="SUCCESS")
    except Exception as e:
        log(f"Error processing video metadata: {str(e)}", level="ERROR")

# ====================> Cell 2 <===================== #

# @title 🧮 Calculate Split Config (by Size or Duration)
# @markdown - Enter `target_value` as **GB** if mode is `"by_size"`, or in **minutes** if mode is `"by_duration"`.

# 📥 Input Parameters
mode = "by_size"  # @param ["by_size", "by_duration"]
target_value = 1  # @param {type:"number"}
telegram_mode = False  # @param ["False", "True"] {type:"raw"}
metadata_path = ""  # @param {type:"string"}
output_json_path = "/content/media_toolkit/metadata/calc.json"  # @param {type:"string"}

import json
import os
import math


# ✅ Logger
def log(message, level="INFO"):
    print(f"[{level}] {message}")


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours} h")
    if minutes > 0:
        parts.append(f"{minutes} m")
    if sec > 0 or not parts:
        parts.append(f"{sec} s")
    return " ".join(parts)


# 🖥 Show Summary (keeps original print format with icons)
def show_split_summary(config: dict):
    filename = os.path.basename(config.get("input_video_path", "unknown"))
    duration_sec = int(config.get("duration_sec", 0))
    duration_str = format_duration(duration_sec)
    size_mb = round(config.get("target_size_mb", 0), 2)
    telegram_mode = config.get("telegram_mode", False)
    will_split = config.get("will_split", False)
    parts = config.get("estimated_parts", 1)
    path = config.get("input_video_path", "N/A")

    print(f"╭📄 Filename         : {filename}")
    print(f"├⏰ Total Duration   : {duration_sec} sec / {duration_str}")
    print(f"├📦 Target Size      : {size_mb} MB")
    print(f"├📤 Telegram Mode    : {telegram_mode}")
    print(f"├✂️ Will Split       : {will_split}")
    print(f"├🔢 Estimated Parts  : {parts}")
    print(f"╰📁 Video Path       : {path}")


# 📂 Load metadata
def load_metadata_from_file(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"Failed to load metadata: {str(e)}", level="ERROR")
        raise


# 🔧 Calculate from size
def calculate_max_duration(metadata: dict, target_mb: float, telegram_mode: bool):
    size_mb = float(metadata["format"]["size"]) / (1024 * 1024)
    duration_sec = float(metadata["format"]["duration"])
    bitrate_kbps = float(metadata["format"]["bit_rate"]) / 1000

    if telegram_mode and target_mb > 1900:
        target_mb = 1900
        log("Telegram mode enabled - capping target size at 1900MB", level="INFO")

    if size_mb <= target_mb:
        return duration_sec, size_mb, target_mb, duration_sec, False
    else:
        max_duration_sec = (target_mb * 8 * 1024) / bitrate_kbps
        return max_duration_sec, size_mb, target_mb, duration_sec, True


# 🔧 Calculate from duration
def estimate_size_by_duration(metadata: dict, input_min: float, telegram_mode: bool):
    duration_sec = float(metadata["format"]["duration"])
    bitrate_kbps = float(metadata["format"]["bit_rate"]) / 1000
    max_duration_sec = input_min * 60

    if max_duration_sec >= duration_sec:
        will_split = False
        max_duration_sec = duration_sec
    else:
        will_split = True

    estimated_size_mb = (bitrate_kbps / 8) * max_duration_sec / 1024

    if telegram_mode and estimated_size_mb > 1900:
        estimated_size_mb = 1900
        max_duration_sec = (1900 * 8 * 1024) / bitrate_kbps
        will_split = max_duration_sec < duration_sec
        log(
            "Telegram mode enabled - adjusting duration to fit 1900MB limit",
            level="INFO",
        )

    return max_duration_sec, estimated_size_mb, duration_sec, will_split


# 🚀 Execute
def main():
    try:
        val = float(target_value)
    except ValueError:
        log("Invalid input: target_value must be a number", level="ERROR")
        return

    if val <= 0:
        log("Invalid input: target_value must be greater than 0", level="ERROR")
        return

    try:
        metadata = load_metadata_from_file(metadata_path)
        video_path = metadata.get("input_video_path")

        if not video_path or not os.path.exists(video_path):
            log("The video file path is missing or does not exist", level="ERROR")
            return

        log(f"Processing video: {os.path.basename(video_path)}")

        if mode == "by_duration":
            log(f"Calculating split by duration: {val} minutes")
            max_duration_sec, estimated_size_mb, duration_sec, will_split = (
                estimate_size_by_duration(metadata, val, telegram_mode)
            )
            target_mb = estimated_size_mb
        else:
            log(f"Calculating split by size: {val} GB")
            target_mb = val * 1024  # Convert GB to MB
            max_duration_sec, video_size_mb, target_mb, duration_sec, will_split = (
                calculate_max_duration(metadata, target_mb, telegram_mode)
            )

        estimated_parts = (
            math.ceil(duration_sec / max_duration_sec) if will_split else 1
        )
        log(f"Estimated parts: {estimated_parts}")

        result = {
            "max_duration_sec": int(max_duration_sec),
            "duration_sec": int(duration_sec),
            "target_size_mb": round(target_mb, 2),
            "telegram_mode": telegram_mode,
            "will_split": will_split,
            "estimated_parts": estimated_parts,
            "input_video_path": video_path,
        }

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        log(f"Split configuration saved to: {output_json_path}", level="SUCCESS")
        show_split_summary(result)

    except Exception as e:
        log(f"An error occurred during processing: {str(e)}", level="ERROR")


if __name__ == "__main__":
    main()

# ===========================> Cell 3 <========================= #

# @title ✂️📦 Split & Merge Video Parts
import os
import sys
import json
import math
import shutil
import subprocess
from importlib import import_module
from tqdm import tqdm


# ✅ Logger
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# ✅ Dependency Check and Installation
required_packages = [("tqdm", "tqdm"), ("ffmpeg", "ffmpeg-python")]


def check_and_install_dependencies():
    missing_packages = []
    for import_name, pkg_name in required_packages:
        try:
            import_module(import_name)
        except ImportError:
            missing_packages.append(pkg_name)

    if missing_packages:
        print("🔧 Installing missing dependencies...")
        try:
            from pip._internal import main as pipmain
        except:
            from pip import main as pipmain

        for pkg in missing_packages:
            pipmain(["install", pkg])
        log("Dependencies installed successfully")
    else:
        log("All dependencies are already installed")


check_and_install_dependencies()

# 📥 Load Config
split_info_path = ""  # @param {type:"string"}
with open(split_info_path) as f:
    info = json.load(f)

video_path = info.get("input_video_path")
if not video_path or not os.path.exists(video_path):
    log(f"Video file does not exist: {video_path}", "ERROR")
    exit()

max_duration_sec = info["max_duration_sec"]
target_size_mb = info["target_size_mb"]
total_duration = info["duration_sec"]

# 📁 Setup Folders
video_dir = os.path.dirname(video_path)
TEMP_DIR = os.path.join(video_dir, "temp")
OUTPUT_DIR = os.path.join(video_dir, "output")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# 🔧 Utilities
def split_video_by_duration(
    video_path, output_dir, base_filename, total_duration, chunk_duration
):
    chunk_paths = []
    for i in tqdm(
        range(0, math.ceil(total_duration), chunk_duration), desc="🎞️ Splitting"
    ):
        chunk_path = os.path.join(output_dir, f"{base_filename}_chunk_{i}.mp4")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    video_path,
                    "-ss",
                    str(i),
                    "-t",
                    str(chunk_duration),
                    "-c",
                    "copy",
                    chunk_path,
                ],
                check=True,
            )
            chunk_paths.append(chunk_path)
        except subprocess.CalledProcessError as e:
            log(f"Failed to split video at {i}s: {e}", "ERROR")
            raise
    return chunk_paths


def get_file_size(path):
    return os.path.getsize(path) / (1024 * 1024)


def group_chunks_by_size(chunks, target_mb):
    groups, current_group, current_size = [], [], 0
    for chunk in chunks:
        size = get_file_size(chunk)
        if current_size + size > target_mb and current_group:
            groups.append(current_group)
            current_group, current_size = [], 0
        current_group.append(chunk)
        current_size += size
    if current_group:
        groups.append(current_group)
    return groups


def merge_chunks(chunk_paths, output_path, temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    list_path = os.path.join(temp_dir, "merge_list.txt")

    # Verify all chunks exist before merging
    for chunk in chunk_paths:
        if not os.path.exists(chunk):
            raise FileNotFoundError(f"Chunk file not found: {chunk}")

    # Write merge list
    with open(list_path, "w") as f:
        for chunk in chunk_paths:
            f.write(f"file '{os.path.abspath(chunk)}'\n")

    # Run ffmpeg with error checking
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_path,
                "-c",
                "copy",
                output_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        if not os.path.exists(output_path):
            raise RuntimeError(f"Merge failed - output file not created: {output_path}")

    except subprocess.CalledProcessError as e:
        log(f"Merge failed with error:\n{e.stderr}", "ERROR")
        raise


# 🚀 Split & Merge
try:
    base_filename = os.path.splitext(os.path.basename(video_path))[0]

    log(f"Splitting into chunks of {max_duration_sec} seconds...")
    all_chunks = split_video_by_duration(
        video_path, TEMP_DIR, base_filename, total_duration, max_duration_sec
    )
    log(f"Chunks created: {len(all_chunks)}")

    groups = group_chunks_by_size(all_chunks, target_size_mb)
    log(f"Total parts to merge: {len(groups)}")

    for i, group in enumerate(groups, 1):
        output_file = os.path.join(OUTPUT_DIR, f"{base_filename}_part_{i:03d}.mp4")
        log(f"Merging {len(group)} chunks into {os.path.basename(output_file)} ...")
        merge_chunks(group, output_file, temp_dir=TEMP_DIR)
        size = get_file_size(output_file)
        log(f"{os.path.basename(output_file)} finished ({size:.2f} MB)", "SUCCESS")

except Exception as e:
    log(f"Processing failed: {str(e)}", "ERROR")
    raise

finally:
    # 🧹 Cleanup
    try:
        shutil.rmtree(TEMP_DIR)
        log(f"Temporary files deleted: {TEMP_DIR}")
    except Exception as e:
        log(f"Failed to clean temporary files: {e}", "WARNING")

log(f"Processing complete for: {os.path.basename(video_path)}")

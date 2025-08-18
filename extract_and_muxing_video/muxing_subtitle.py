# @title 📝 Muxing Subtitle to Video (Softsub MKV)
import subprocess
import shutil
import os


# ✅ Unified Logging
def log(message: str, level: str = "INFO"):
    print(f"[{level}] {message}")


# Check and install ffmpeg if not found
if not shutil.which("ffmpeg"):
    log("ffmpeg not found. Installing via apt...")
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", "ffmpeg"])
    if not shutil.which("ffmpeg"):
        log("ffmpeg installation failed.", "ERROR")
    else:
        log("ffmpeg installed successfully.")

# 📌 Input Paths (Google Colab or Local)
video_input = ""  # @param {type:"string"}
subtitle_input = ""  # @param {type:"string"}
output_folder = "/content/media_toolkit"  # @param {type:"string"}


def is_file(path: str) -> bool:
    return os.path.isfile(path)


# 🔧 Mux a subtitle into a single video file
def mux_subtitle(video_path, subtitle_path, output_path, index=None, total=None):
    if not os.path.exists(video_path):
        log("Video file not found!", "ERROR")
        return
    if not os.path.exists(subtitle_path):
        log("Subtitle file not found!", "ERROR")
        return

    os.makedirs(output_path, exist_ok=True)
    progress = f"[{index+1}/{total}]" if index is not None else ""

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_file = os.path.join(output_path, f"{base_name}_sub.mkv")

    subtitle_ext = os.path.splitext(subtitle_path)[1].lower()
    log(f"{progress} Subtitle type: {subtitle_ext}")
    log(f"{progress} Video: {video_path}")
    log(f"{progress} Subtitle: {subtitle_path}")
    log(f"{progress} Output: {output_file}")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-i",
        subtitle_path,
        "-map",
        "0:v",
        "-map",
        "0:a?",
        "-map",
        "1:s:0",
        "-c",
        "copy",
        "-metadata:s:s:0",
        "language=eng",
        output_file,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"{progress} Subtitle successfully muxed.", "SUCCESS")
    else:
        log(f"{progress} Failed to mux subtitle.", "ERROR")
        print(result.stderr)


# 🚀 Preview pairing sebelum muxing
def preview_pairs(video_files, subtitle_files):
    total = min(len(video_files), len(subtitle_files))
    log("Preview pairing video ↔ subtitle:")
    for i in range(total):
        v = os.path.basename(video_files[i])
        s = os.path.basename(subtitle_files[i])
        print(f"  [{i+1}] {v}  ↔  {s}")
    if len(video_files) != len(subtitle_files):
        log(
            "⚠️ Jumlah video dan subtitle berbeda, hanya diproses hingga jumlah minimum.",
            "WARNING",
        )


# 🚀 Batch process for multiple videos and subtitles
def batch_mux_subtitles(video_input, subtitle_input, output_folder):
    if is_file(video_input):
        video_files = [video_input]
    else:
        video_files = sorted(
            [
                os.path.join(video_input, f)
                for f in os.listdir(video_input)
                if f.lower().endswith((".mp4", ".mkv", ".webm", ".mov"))
            ]
        )

    if is_file(subtitle_input):
        subtitle_files = [subtitle_input]
    else:
        subtitle_files = sorted(
            [
                os.path.join(subtitle_input, f)
                for f in os.listdir(subtitle_input)
                if f.lower().endswith((".srt", ".vtt", ".ass", ".ssa", ".sub", ".txt"))
            ]
        )

    log("Starting batch subtitle muxing...")
    log(f"Video files found: {len(video_files)}")
    log(f"Subtitle files found: {len(subtitle_files)}")

    # 🔍 Preview pasangan sebelum diproses
    preview_pairs(video_files, subtitle_files)

    total = min(len(video_files), len(subtitle_files))
    os.makedirs(output_folder, exist_ok=True)

    for i in range(total):
        mux_subtitle(
            video_files[i], subtitle_files[i], output_folder, index=i, total=total
        )

    log("All files have been successfully muxed with subtitles.", "SUCCESS")


# 🚀 Run the batch muxing
batch_mux_subtitles(video_input, subtitle_input, output_folder)

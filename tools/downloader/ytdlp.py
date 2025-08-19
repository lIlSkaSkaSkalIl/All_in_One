# @title 🔽 Download File via Direct Link (yt-dlp)

# ==========================
# 📦 INSTALL DEPENDENCIES
# ==========================
import logging
import os
import subprocess
import time
from datetime import datetime
from urllib.parse import urlparse
import re
import requests
import sys


def log(message, level="INFO"):
    print(f"[{level}] {message}")


def install_ytdlp():
    """Install yt-dlp if not already installed"""
    try:
        subprocess.run(
            ["yt-dlp", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log("yt-dlp is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("Installing yt-dlp...")
        result = subprocess.run(
            ["pip", "install", "-q", "yt-dlp"], capture_output=True, text=True
        )
        if result.returncode == 0:
            log("yt-dlp installed successfully")
        else:
            log("Failed to install yt-dlp", "ERROR")
            log(result.stderr)
            raise RuntimeError("Failed to install yt-dlp")


install_ytdlp()

# ==========================
# ⚙️ INPUT CONFIGURATION
# ==========================
download_url = ""  # @param {type:"string"}
filename = ""  # @param {type:"string"}
output_dir = "/content/downloads"  # @param {type:"string"}
retry_count = 3  # @param {type:"integer", min:1, max:10}


# ==========================
# 🧠 HELPER FUNCTIONS
# ==========================
def sanitize_filename(name: str, max_length: int = 255) -> str:
    name = re.sub(r'[\/:*?"<>|]', "_", name)
    if len(name) > max_length:
        base, ext = os.path.splitext(name)
        name = base[: max_length - len(ext)] + ext
    return name.strip()


def get_output_filename(url: str, fallback_name: str) -> str:
    if fallback_name.strip():
        return sanitize_filename(fallback_name.strip())
    try:
        head_resp = requests.head(url, allow_redirects=True, timeout=10)
        if "Content-Disposition" in head_resp.headers:
            cd = head_resp.headers["Content-Disposition"]
            fname_match = re.findall('filename="?([^"]+)"?', cd)
            if fname_match:
                return sanitize_filename(fname_match[0])
    except Exception as e:
        log(f"Could not fetch filename from header: {e}", "WARNING")
    basename = os.path.basename(urlparse(url).path)
    if basename:
        return sanitize_filename(basename)
    return f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def print_download_summary(
    download_url: str, final_filename: str, output_path: str, retry_count: int
):
    print(f"╭🎯 URL       : {download_url}")
    print(f"├💾 Filename  : {final_filename}")
    print(f"├📁 Location  : {output_path}")
    print(f"╰🔄 Retries   : {retry_count}")


def print_download_result(
    final_filename: str, download_url: str, output_path: str, elapsed: float
):
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n✅ Download Completed!")
        print("╭📄 Filename   :", final_filename)
        print("├🌐 URL        :", download_url)
        print(f"├📦 File Size  : {file_size:.2f} MB")
        print(f"╰⏱️ Duration   : {elapsed:.2f} seconds")
    else:
        print(f"\n❌ Status: Download Failed!")
        print(f"ℹ️ Reason: File not found after download")


def verify_downloaded_file(file_path: str, min_size_kb: int = 100):
    if not os.path.exists(file_path):
        return False
    try:
        file_size = os.path.getsize(file_path)
        if file_size < min_size_kb * 1024:
            log(f"File too small ({file_size} bytes), possibly corrupted", "WARNING")
            os.remove(file_path)
            return False
        return True
    except Exception as e:
        log(f"File verification failed: {str(e)}", "ERROR")
        return False


def format_speed(speed_bytes):
    """Format download speed in human-readable format"""
    for unit in ["B/s", "KB/s", "MB/s", "GB/s"]:
        if speed_bytes < 1024:
            return f"{speed_bytes:.2f} {unit}"
        speed_bytes /= 1024
    return f"{speed_bytes:.2f} TB/s"


# ==========================
# 🚀 MAIN DOWNLOAD FUNCTION
# ==========================
def download_file(download_url: str, filename: str, output_dir: str, retry_count: int):
    os.makedirs(output_dir, exist_ok=True)
    final_filename = get_output_filename(download_url, filename)
    output_path = os.path.join(output_dir, final_filename)

    print_download_summary(download_url, final_filename, output_path, retry_count)

    try:
        start_time = time.time()
        cmd = [
            "yt-dlp",
            "--no-part",  # langsung simpan tanpa .part
            "--progress",  # Enable progress display
            "--newline",  # Force progress in new lines
            "--retries",
            str(retry_count),
            "-o",
            output_path,
            download_url,
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Process output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                # Clean and display the progress
                output = output.strip()
                if "[download]" in output:
                    # Extract progress information
                    progress_info = output.split("[download]")[-1].strip()
                    log(f"{progress_info}", flush=True)

        # Check for errors
        if process.returncode != 0:
            error_output = process.stderr.read()
            log(f"yt-dlp failed: {error_output}", "ERROR")
            raise RuntimeError("Download process failed")

        elapsed = time.time() - start_time
        print()  # New line after progress display
        print_download_result(final_filename, download_url, output_path, elapsed)

        if not verify_downloaded_file(output_path):
            raise RuntimeError("Downloaded file verification failed")

        return output_path

    except Exception as e:
        log(f"Download failed: {str(e)}", "ERROR")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise


# ==========================
# ✅ EXECUTE DOWNLOAD
# ==========================
download_file(download_url, filename, output_dir, retry_count)

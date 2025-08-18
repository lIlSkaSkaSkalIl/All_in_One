# @title 📥 Torrent Downloader via aria2c
# @markdown - Enter the magnet link and output directory
magnet_link = ""  # @param {type:"string"}
output_dir = ""  # @param {type:"string"}

import os
import re
import subprocess
import shutil


# ========== 🔧 Custom Logging ==========
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# ========== 🧹 Remove sample_data if exists ==========
def remove_sample_data():
    sample_path = "/content/sample_data"
    if os.path.exists(sample_path):
        shutil.rmtree(sample_path)
        log("Folder /content/sample_data has been removed.")
    else:
        log("No /content/sample_data folder found.")


# ========== 📦 Install aria2 if not installed ==========
def ensure_aria2_installed():
    if shutil.which("aria2c") is None:
        log("aria2c not found. Installing aria2...")
        result = subprocess.run(
            ["apt-get", "install", "-y", "aria2"], capture_output=True, text=True
        )
        if result.returncode == 0:
            log("aria2 successfully installed.")
        else:
            log("Failed to install aria2.", level="ERROR")
            log(result.stderr.strip(), level="ERROR")
            raise RuntimeError("aria2 installation failed.")
    else:
        log("aria2c is already installed.")


# ========== 📂 Ensure output directory exists ==========
def ensure_output_dir(path):
    if not os.path.exists(path):
        log(f"Creating output directory: {path}")
        os.makedirs(path)
    else:
        log(f"Output directory already exists: {path}")


# ========== 🔄 Download torrent via magnet ==========
def download_torrent(magnet_link, output_path):
    log("Starting torrent download via magnet link...")
    command = [
        "aria2c",
        "--enable-color=false",
        "--dir",
        output_path,
        "--seed-time=0",
        "--summary-interval=1",
        "--console-log-level=warn",
        "--max-connection-per-server=16",
        "--split=16",
        "--bt-max-peers=80",
        "--bt-request-peer-speed-limit=0",
        "--bt-enable-lpd=true",
        "--bt-save-metadata=true",
        "--bt-metadata-only=false",
        magnet_link,
    ]

    log(f"Running command: {' '.join(command)}")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        current_filename = None

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            if line.startswith("FILE:"):
                file_info = line.split("FILE:", 1)[1].strip()

                if "/" in file_info:
                    file_info = file_info.split("/")[-1]

                words = re.split(r"[.\s]", file_info)
                short_name = ".".join(words[:3])

                current_filename = short_name

            elif line.startswith("[#"):
                if current_filename:
                    log(f"{current_filename}: {line}")

        process.wait()
        if process.returncode == 0:
            log("Download completed successfully.")
        else:
            log(f"aria2c exited with error code: {process.returncode}", level="ERROR")

    except Exception as e:
        log(f"An error occurred while running aria2c: {e}", level="ERROR")


# ========== 🚀 Execute ==========
remove_sample_data()
ensure_aria2_installed()
ensure_output_dir(output_dir)
download_torrent(magnet_link, output_dir)

# @title 🚀 MEGA Downloader (File & Folder)
from datetime import datetime
import subprocess
import os
import shutil
import sys
import time

# ===================== USER INPUT =====================
mega_type = "file"  # @param ["file", "folder"] {allow-input: false}
mega_link = ""  # @param {type:"string"}
output_path = "/content/media_toolkit/mega_download"  # @param {type:"string"}
timeout_minutes = 60  # @param {type:"integer", min:1, max:240}
min_disk_space_mb = 100  # @param {type:"integer", min:10}
show_logs = True  # @param {type:"boolean"}
# =====================================================


# =================== CUSTOM LOGGING ====================
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# =============== CONFIG ====================
class Config:
    DEFAULT_TIMEOUT = timeout_minutes * 60
    MIN_DISK_SPACE = min_disk_space_mb * 1024 * 1024  # in bytes


# =============== DISK & VALIDATION ====================
def check_disk_space(path: str) -> bool:
    try:
        stat = shutil.disk_usage(path)
        free = stat.free
        if free < Config.MIN_DISK_SPACE:
            log(
                f"Insufficient disk space: {free/1024/1024:.2f}MB available, {min_disk_space_mb}MB required.",
                level="ERROR",
            )
            return False
        log(f"Disk space OK: {free/1024/1024:.2f}MB available")
        return True
    except Exception as e:
        log(f"Failed to check disk space: {e}", level="ERROR")
        return False


def validate_url(url: str) -> bool:
    return url.startswith(("https://mega.nz/", "mega://"))


# =============== INSTALL TOOLS ====================
def install_megatools() -> bool:
    log("Checking megatools...")
    try:
        subprocess.run(
            ["megadl", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except:
        try:
            subprocess.run(["apt-get", "update", "-y"], check=True)
            subprocess.run(["apt-get", "install", "-y", "megatools"], check=True)
            log("Megatools installed successfully")
            return True
        except Exception as e:
            log(f"Failed to install megatools: {e}", level="ERROR")
            return False


# =============== DOWNLOAD FILE ====================
def download_file(url: str, path: str) -> bool:
    log(f"Starting file download: {url}")
    try:
        cmd = ["megadl", "--path", path, url]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        last_line = ""
        for line in proc.stdout:
            line = line.strip()
            if line:
                log(line)
                last_line = line
        print()  # newline
        exit_code = proc.wait()
        if exit_code == 0:
            log("File download complete")
            return True
        else:
            log("File download failed", level="ERROR")
            return False
    except Exception as e:
        log(f"Error during file download: {e}", level="ERROR")
        return False


# =============== DOWNLOAD FOLDER ====================
def download_folder(url: str, path: str) -> bool:
    log(f"Starting folder download: {url}")
    try:
        os.makedirs(path, exist_ok=True)
        cmd = ["megadl", "--path", path, url]

        start = time.time()
        if show_logs:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            for line in proc.stdout:
                line = line.strip()
                if line:
                    if output_path in line:
                        log(line, "FILE")
                    else:
                        log(line, "DOWNLOAD")

            print()  # newline
            proc.wait()
        else:
            subprocess.run(cmd, check=True, timeout=Config.DEFAULT_TIMEOUT)

        elapsed = time.time() - start
        log(f"Folder download completed in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        log(f"Folder download failed: {e}", level="ERROR")
        return False


# =============== MAIN ====================
def main():
    log("Starting MEGA Downloader")
    log(f"Link: {mega_link}")
    log(f"Output Path: {output_path}")
    log(
        f"Mode: {mega_type.upper()} | Timeout: {timeout_minutes} minutes | Min Space: {min_disk_space_mb}MB"
    )

    if not validate_url(mega_link):
        log("Invalid MEGA link format.", level="ERROR")
        return

    os.makedirs(output_path, exist_ok=True)
    if not check_disk_space(output_path):
        return

    if not install_megatools():
        return

    if mega_type == "file":
        success = download_file(mega_link, output_path)
    elif mega_type == "folder":
        success = download_folder(mega_link, output_path)
    else:
        log("Unknown download type selected.", level="ERROR")
        return

    if success:
        log("Download task completed successfully.")
    else:
        log("Download task failed.", level="ERROR")


main()

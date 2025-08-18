# @title 🔽 Download File via Direct Link

# ==========================
# 📦 INSTALL DEPENDENCIES
# ==========================
import logging
import os
import subprocess
import time
from datetime import datetime
from urllib.parse import urlparse
from IPython.display import clear_output


def log(message, level="INFO"):
    print(f"[{level}] {message}")


def install_aria2():
    """Install aria2 if not already installed"""
    try:
        subprocess.run(
            ["aria2c", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log("aria2 is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("Installing aria2...")
        result = subprocess.run(
            ["apt-get", "-qq", "install", "-y", "aria2"], capture_output=True, text=True
        )
        if result.returncode == 0:
            log("aria2 installed successfully")
        else:
            log("Failed to install aria2", "ERROR")
            log(result.stderr)
            raise RuntimeError("Failed to install aria2")


install_aria2()

# ==========================
# ⚙️ INPUT CONFIGURATION
# ==========================
download_url = ""  # @param {type:"string"}
filename = ""  # @param {type:"string"}
output_dir = "/content/downloads"  # @param {type:"string"}
aria2_parallel_conn = 10  # @param {type:"integer"}
retry_count = 3  # @param {type:"integer", min:1, max:10}
timeout = 600  # @param {type:"integer", min:60, max:3600}

# ==========================
# 🧠 HELPER FUNCTIONS
# ==========================
import re
import requests


def sanitize_filename(name: str, max_length: int = 255) -> str:
    # Hapus karakter ilegal untuk nama file
    name = re.sub(r'[\/:*?"<>|]', "_", name)
    # Potong jika terlalu panjang
    if len(name) > max_length:
        base, ext = os.path.splitext(name)
        name = base[: max_length - len(ext)] + ext
    return name.strip()


def get_output_filename(url: str, fallback_name: str) -> str:
    # 1️⃣ Prioritas pertama: filename dari parameter user
    if fallback_name.strip():
        return sanitize_filename(fallback_name.strip())

    # 2️⃣ Coba ambil dari Content-Disposition header
    try:
        head_resp = requests.head(url, allow_redirects=True, timeout=10)
        if "Content-Disposition" in head_resp.headers:
            cd = head_resp.headers["Content-Disposition"]
            fname_match = re.findall('filename="?([^"]+)"?', cd)
            if fname_match:
                return sanitize_filename(fname_match[0])
    except Exception as e:
        log(f"Could not fetch filename from header: {e}", "WARNING")

    # 3️⃣ Ambil dari URL path
    basename = os.path.basename(urlparse(url).path)
    if basename:
        return sanitize_filename(basename)

    # 4️⃣ Fallback terakhir: generate nama otomatis
    return f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def validate_parallel_connections(conn: int) -> int:
    if conn < 1:
        log("Parallel connection < 1. Using 1 instead.", "WARNING")
        return 1
    elif conn > 16:
        log("Parallel connection > 16. Using 16 instead.", "WARNING")
        return 16
    return conn


def print_download_summary(
    download_url: str,
    final_filename: str,
    output_path: str,
    aria2_parallel_conn: int,
    retry_count: int,
    timeout: int,
):
    print(f"╭🎯 URL         : {download_url}")
    print(f"├💾 Filename    : {final_filename}")
    print(f"├📁 Location    : {output_path}")
    print(f"├⚙️ Connections : {aria2_parallel_conn}")
    print(f"├🔄 Retries     : {retry_count}")
    print(f"╰⏱️ Timeout     : {timeout} seconds\n")


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


def cleanup_resources(process, output_path: str = None):
    try:
        if process and process.poll() is None:
            process.terminate()
        if process:
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
        if output_path and os.path.exists(output_path):
            if os.path.getsize(output_path) == 0:
                os.remove(output_path)
    except Exception as e:
        log(f"Cleanup warning: {str(e)}", "WARNING")


def display_download_progress(process):
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            line = output.strip()
            if line.startswith("[#"):
                # print(line, flush=True)
                log(f"{line}", "DOWNLOAD")
            elif "error" in line.lower():
                log(f"{line}", "ERROR")
            elif "warn" in line.lower():
                log(f"{line}", "WARNING")
            elif "download completed" in line.lower():
                log(f"{line}")

    if process.stderr:
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"\n🔴 Error details:\n{stderr_output.strip()}")


def run_download_process(
    download_url: str,
    output_dir: str,
    final_filename: str,
    aria2_parallel_conn: int,
    retry_count: int,
    timeout: int,
):
    cmd = [
        "aria2c",
        download_url,
        "-x",
        str(aria2_parallel_conn),
        "-s",
        str(aria2_parallel_conn),
        "-k",
        "1M",
        "-d",
        output_dir,
        "-o",
        final_filename,
        "--max-tries=" + str(retry_count),
        "--timeout=" + str(timeout),
        "--summary-interval=1",
        "--console-log-level=warn",
        "--file-allocation=none",
        "--auto-file-renaming=false",
        "--allow-overwrite=true",
    ]

    try:
        log("Starting download with aria2c...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        return process
    except Exception as e:
        log(f"Failed to start download process: {str(e)}", "ERROR")
        raise RuntimeError("Download process initialization failed")


# ==========================
# 🚀 MAIN DOWNLOAD FUNCTION
# ==========================
def download_file(
    download_url: str,
    filename: str,
    output_dir: str,
    aria2_parallel_conn: int,
    retry_count: int,
    timeout: int,
):
    os.makedirs(output_dir, exist_ok=True)
    aria2_parallel_conn = validate_parallel_connections(aria2_parallel_conn)
    final_filename = get_output_filename(download_url, filename)
    output_path = os.path.join(output_dir, final_filename)

    print_download_summary(
        download_url,
        final_filename,
        output_path,
        aria2_parallel_conn,
        retry_count,
        timeout,
    )

    process = None
    try:
        start_time = time.time()
        process = run_download_process(
            download_url,
            output_dir,
            final_filename,
            aria2_parallel_conn,
            retry_count,
            timeout,
        )

        try:
            display_download_progress(process)
            process.wait(timeout=timeout * 2)
        except subprocess.TimeoutExpired:
            logger.error(f"Download timed out after {timeout*2} seconds")
            raise

        elapsed = time.time() - start_time
        print_download_result(final_filename, download_url, output_path, elapsed)

        if not verify_downloaded_file(output_path):
            raise RuntimeError("Downloaded file verification failed")

        return output_path

    except KeyboardInterrupt:
        log("Download interrupted by user", "WARNING")
        raise
    except Exception as e:
        log(f"Download failed: {str(e)}", "ERROR")
        if os.path.exists(output_path):
            os.remove(output_path)
        raise
    finally:
        cleanup_resources(process, output_path)


# ==========================
# ✅ EXECUTE DOWNLOAD
# ==========================
download_file(
    download_url, filename, output_dir, aria2_parallel_conn, retry_count, timeout
)

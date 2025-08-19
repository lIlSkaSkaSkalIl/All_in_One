# @title ⚙️ Compress / Decompress

import os
import shutil
import sys

REPO_URL = "https://github.com/lIlSkaSkaSkalIl/compress_decompress_archive.git"
REPO_ROOT = "/content/compress_decompress_archive"


def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# 🔁 Delete and re-clone if the folder already exists
if os.path.exists(REPO_ROOT):
    log(f"Repository found at {REPO_ROOT}, removing...", level="WARNING")
    shutil.rmtree(REPO_ROOT)

log(f"Cloning repository: {REPO_URL}", level="INFO")
os.system(f"git clone {REPO_URL} {REPO_ROOT}")

# ➕ Add to sys.path if not already
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)
    log(f"Repository path added to sys.path: {REPO_ROOT}", level="INFO")
else:
    log("Repository path already exists in sys.path", level="INFO")

log("Repository is ready to use.", level="INFO")

from tools.archive_tool import run_tool
import os

# @markdown Add filename in `output_path` for compression
# @markdown `/content/media_toolkit/filename`
metode = (
    "unzip"  # @param ["zip", "unzip", "rar", "unrar", "7z", "un7z", "tar", "untar"]
)
tar_method = "none"  # @param ["gz", "xz", "none"]
input_path = ""  # @param {type:"string"}
output_path = "/content/media_toolkit"  # @param {type:"string"}

os.makedirs(output_path, exist_ok=True)

# 🚀 Jalankan proses
if metode == "tar":
    run_tool(metode, input_path, output_path, tar_method=tar_method)
else:
    run_tool(metode, input_path, output_path)

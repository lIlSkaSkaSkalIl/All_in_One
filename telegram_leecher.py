# @title <font color=red> 🖥️ Main Colab Leech Code

# @markdown <div><center><img src="https://user-images.githubusercontent.com/125879861/255391401-371f3a64-732d-4954-ac0f-4f093a6605e1.png" height=80></center></div>
# @markdown <center><h4><a href="https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS">READ</a><b> How to use</b></h4></center>
# @markdown <br><center><h2><font color=lime><strong>Fill all Credentials, Run The Cell and Start The Bot</strong></h2></center>
# @markdown <br><br>

API_ID = 123  # @param {type: "integer"}
API_HASH = ""  # @param {type: "string"}
BOT_TOKEN = ""  # @param {type: "string"}
USER_ID = 123  # @param {type: "integer"}
DUMP_ID = -123  # @param {type: "integer"}

import subprocess, json, shutil, os, logging
from IPython.display import clear_output

# ===================== PROFESSIONAL LOGGING SETUP =====================
def setup_logging():
    """Configure professional logging for Colab environment"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create and configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(levelname)s:%(message)s'
    ))
    logger.addHandler(handler)
    return logger

logger = setup_logging()

# ===================== ORIGINAL CODE WITH IMPROVED LOGGING =====================

logger.info("Initializing setup...")

# Format DUMP_ID if necessary
if DUMP_ID and len(str(DUMP_ID)) == 10 and "-100" not in str(DUMP_ID):
    logger.info(f"Formatting DUMP_ID: adding -100 prefix to {DUMP_ID}")
    DUMP_ID = int("-100" + str(DUMP_ID))

# Remove default Colab sample data
if os.path.exists("/content/sample_data"):
    logger.info("Removing default Colab sample data directory")
    shutil.rmtree("/content/sample_data")

# URL repo Telegram-Leecher
repo_url = "https://github.com/lIlSkaSkaSkalIl/Telegram-Leecher"
repo_name = "Telegram-Leecher"

# Remove folder if already exists
if os.path.exists(repo_name):
    logger.info(f"Existing '{repo_name}' folder found - removing before clone")
    shutil.rmtree(repo_name)

# Clone the Telegram-Leecher repository
logger.info(f"Cloning repository from {repo_url}")
clone_result = subprocess.run(["git", "clone", repo_url], capture_output=True, text=True)
if clone_result.returncode != 0:
    logger.error(f"Failed to clone repository: {clone_result.stderr}")
    raise RuntimeError("Repository cloning failed")

# Install system dependencies
logger.info("Installing system dependencies (ffmpeg, aria2)")
install_result = subprocess.Popen(
    "apt install ffmpeg aria2 -y",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Display output with proper logging
while True:
    line = install_result.stdout.readline()
    if not line:
        break
    if line.strip():
        logger.info(line.strip())

install_result.wait()

if install_result.returncode != 0:
    logger.error("System dependencies installation failed")
    for line in install_result.stderr:
        logger.error(line.strip())

# Checking Megatools
logger.info("Install megatools...")
install_megatools = subprocess.Popen(
    "apt-get install -y megatools",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

while True:
    line = install_megatools.stdout.readline()
    if not line:
        break
    if line.strip():
        logger.info(line.strip())

install_megatools.wait()

# Install Python dependencies
logger.info("Installing Python dependencies from requirements.txt")
req_path = "/content/Telegram-Leecher/requirements.txt"
process = subprocess.Popen(
    ["pip3", "install", "-r", req_path],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

# Display pip output with proper logging
for line in process.stdout:
    logger.info(line.strip())

process.wait()
if process.returncode != 0:
    logger.error("Python dependencies installation failed")

# Save credentials to JSON
logger.info("Saving credentials to credentials.json")
credentials = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "BOT_TOKEN": BOT_TOKEN,
    "USER_ID": USER_ID,
    "DUMP_ID": DUMP_ID,
}

try:
    with open('/content/Telegram-Leecher/credentials.json', 'w') as file:
        json.dump(credentials, file, indent=4)
    logger.info("Credentials saved successfully")
except Exception as e:
    logger.error(f"Failed to save credentials: {str(e)}")
    raise

# Remove previous bot session if exists
session_path = "/content/Telegram-Leecher/my_bot.session"
if os.path.exists(session_path):
    logger.info("Removing previous bot session file")
    os.remove(session_path)

clear_output()
logger.info("Launching Telegram Leecher bot")

# Run the bot
!cd /content/Telegram-Leecher/ && python3 -m colab_leecher  # type: ignore
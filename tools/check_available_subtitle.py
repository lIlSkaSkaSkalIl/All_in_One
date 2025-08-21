# @title Checking Available Subtitle

import subprocess
import logging
import shutil


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


logger = setup_logging()


def ensure_mkvtoolnix():
    """Install mkvtoolnix if mkvmerge is not available"""
    if shutil.which("mkvmerge") is None:
        logger.info("mkvmerge not found, installing mkvtoolnix...")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(
            ["apt-get", "-y", "install", "mkvtoolnix", "mkvtoolnix-gui"], check=True
        )
    else:
        logger.info("mkvmerge is already installed.")


def list_subtitles(mkv_file):
    try:
        ensure_mkvtoolnix()

        # Jalankan mkvmerge untuk list track
        result = subprocess.run(
            ["mkvmerge", "-i", mkv_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"mkvmerge error: {result.stderr}")
            return

        lines = result.stdout.strip().split("\n")
        subtitle_tracks = [line for line in lines if "subtitles" in line.lower()]

        if not subtitle_tracks:
            logger.info("No subtitle tracks found.")
        else:
            logger.info(f"Found {len(subtitle_tracks)} subtitle track(s):")
            for track in subtitle_tracks:
                logger.info(track)

    except Exception as e:
        logger.error(f"Failed to detect subtitles: {e}")


# Contoh jalankan
mkv_file = ""  # @param {type:"string"}
list_subtitles(mkv_file)

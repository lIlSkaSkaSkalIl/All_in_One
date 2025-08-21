# @title 📂 Move Files or Folder
source_path = "/content/media_toolkit"  # @param {type:"string"}
target_folder = "/content/media_toolkit/video"  # @param {type:"string"}
move_mode = ""  # @param ["", "flat", "recursive"] {allow-input: false}

import os
import shutil
import logging


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    return logger


logger = setup_logging()


def move_path(src, dst, mode=""):
    if not os.path.exists(src):
        logger.error(f"Source path not found: {src}")
        return

    os.makedirs(dst, exist_ok=True)
    moved_count = 0

    # Jika src berupa file tunggal
    if os.path.isfile(src):
        try:
            shutil.move(src, os.path.join(dst, os.path.basename(src)))
            moved_count += 1
            logger.info(f"Moved file: {os.path.basename(src)}")

            # Kalau user isi mode meskipun file → kasih warning
            if mode:
                logger.warning(
                    "Mode parameter ignored because source is a single file."
                )
        except Exception as e:
            logger.error(f"Failed to move file {src}: {e}")

    # Jika src berupa folder
    elif os.path.isdir(src):
        if mode == "":
            logger.warning(
                "Mode not selected. Defaulting to 'flat' mode for folder input."
            )
            mode = "flat"

        if mode == "flat":
            # Hanya file di folder utama
            for file_name in os.listdir(src):
                file_path = os.path.join(src, file_name)
                if os.path.isfile(file_path):
                    try:
                        shutil.move(file_path, os.path.join(dst, file_name))
                        moved_count += 1
                    except Exception as e:
                        logger.error(f"Failed to move {file_name}: {e}")

        elif mode == "recursive":
            # Preserve structure → semua file dipindah dengan subfoldernya
            for root, _, files in os.walk(src):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(root, src)  # supaya struktur ikut dibawa
                    target_subdir = os.path.join(dst, rel_path)
                    os.makedirs(target_subdir, exist_ok=True)
                    try:
                        shutil.move(file_path, os.path.join(target_subdir, file_name))
                        moved_count += 1
                    except Exception as e:
                        logger.error(f"Failed to move {file_name}: {e}")

    logger.info(f"Moved {moved_count} file(s)")
    logger.info(f"Mode : {mode if os.path.isdir(src) else 'ignored (file input)'}")
    logger.info(f"From : {src}")
    logger.info(f"To   : {dst}")


# Jalankan pemindahan
move_path(source_path, target_folder, move_mode)

# @title 📂 Move Files with Options
source_path = ""  # @param {type:"string"}
target_folder = ""  # @param {type:"string"}
mode = "folder"  # @param ["file", "folder", "folder and subfolder(all)"]

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


def move_single_file(src, dst):
    """Move one file"""
    if not os.path.isfile(src):
        logger.error(f"Source is not a file: {src}")
        return 0
    os.makedirs(dst, exist_ok=True)
    try:
        shutil.move(src, os.path.join(dst, os.path.basename(src)))
        logger.info(f"Moved file: {src} -> {dst}")
        return 1
    except Exception as e:
        logger.error(f"Failed to move {src}: {e}")
        return 0


def move_folder_files(src, dst):
    """Move files in a folder (no subfolder)"""
    if not os.path.isdir(src):
        logger.error(f"Source is not a folder: {src}")
        return 0
    os.makedirs(dst, exist_ok=True)
    moved = 0
    for file_name in os.listdir(src):
        file_path = os.path.join(src, file_name)
        if os.path.isfile(file_path):
            try:
                shutil.move(file_path, os.path.join(dst, file_name))
                moved += 1
            except Exception as e:
                logger.error(f"Failed to move {file_name}: {e}")
    return moved


def move_folder_all(src, dst):
    """Move files in a folder including subfolders"""
    if not os.path.isdir(src):
        logger.error(f"Source is not a folder: {src}")
        return 0
    os.makedirs(dst, exist_ok=True)
    moved = 0
    for root, _, files in os.walk(src):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(root, src)  # preserve subfolder structure
            target_dir = os.path.join(dst, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            try:
                shutil.move(src_file, os.path.join(target_dir, file))
                moved += 1
            except Exception as e:
                logger.error(f"Failed to move {src_file}: {e}")
    return moved


# 🚀 Run based on mode
moved_count = 0
if mode == "file":
    moved_count = move_single_file(source_path, target_folder)
elif mode == "folder":
    moved_count = move_folder_files(source_path, target_folder)
elif mode == "folder and subfolder(all)":
    moved_count = move_folder_all(source_path, target_folder)
else:
    logger.error(f"Unknown mode: {mode}")

logger.info(f"Total moved: {moved_count}")
logger.info(f"Target folder: {target_folder}")

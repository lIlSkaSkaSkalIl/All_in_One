# @title 🧹 Delete Folder or Files
folder_path = ""  # @param {type:"string"}
delete_exts = ""  # @param ["", ".txt", ".mp4,.mkv", ".jpg,.png"] {allow-input: true}

import os
import shutil
import logging


def setup_logging():
    """Configure professional logging for Colab environment"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
    return logger


logger = setup_logging()


def format_size(bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"


def print_folder_summary(folder):
    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(folder):
        for file in files:
            total_files += 1
            try:
                filepath = os.path.join(root, file)
                total_size += os.path.getsize(filepath)
            except:
                pass

    logger.info("Folder Summary:")
    logger.info(f"Total files : {total_files}")
    logger.info(f"Total size  : {format_size(total_size)}")
    logger.info(f"Folder path : {folder}")


def delete_files_by_extensions(folder, extensions):
    extensions = [ext.strip().lower() for ext in extensions if ext.strip()]
    deleted_count = 0
    deleted_size = 0

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                try:
                    deleted_size += os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete {filepath}: {e}")

    logger.info(
        f"Deleted {deleted_count} file(s) with extensions {extensions} ({format_size(deleted_size)})"
    )


def delete_entire_folder(folder):
    if not os.path.exists(folder):
        logger.error(f"Folder not found: {folder}")
        return

    if not os.path.isdir(folder):
        logger.warning(f"Not a folder: {folder}")
        return

    print_folder_summary(folder)
    logger.info("Deleting entire folder...")

    try:
        shutil.rmtree(folder)
        logger.info(f"Folder deleted successfully: {folder}")
    except Exception as e:
        logger.error(f"Failed to delete folder: {e}")


# Eksekusi utama
if delete_exts.strip():
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print_folder_summary(folder_path)
        delete_files_by_extensions(folder_path, delete_exts.split(","))
    else:
        logger.error(f"Folder not found or invalid: {folder_path}")
else:
    delete_entire_folder(folder_path)
